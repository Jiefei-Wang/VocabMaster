import base64
import pandas as pd
import math
import uuid

from dateutil.parser import parse

from .models import *
from .database_api import *
from .keys import *
from .dictionary_api import updateWordDatabase, loadPronounce
from .prediction import predictNextWordsLogistic

#####################################################
# Utilities
#####################################################
def removeNoneItems(dictObj):
    return {k: v for k, v in dictObj.items() if v is not None}


def formatWordDefinition(word, language, source):
    if not existsWordDB(word=word, language=language, source=source):
        return None
    obj = getWordsDB(word=word, language=language, source=source).first()
    data = obj.meanings
    return data

def formatSoundmark(word, region):
    if not existsPronounceDB(word=word, region=region):
        return None
    obj = getPronouncesDB(word=word, region=region).first()
    return obj.soundmark

def formatUserInfo(user):
    if user!=None:
        obj = getUserInfoDB(user)
        glossaryBookName = obj.glossaryBook.bookName
        exerciseBookName = obj.exerciseBook.bookName
    else:
        obj = defaultUserValue
        glossaryBookName = defaultUserValue.glossaryBookName
        exerciseBookName = defaultUserValue.exerciseBook
        
    data={
        'user': user,
        'glossaryBook': glossaryBookName,
        'exerciseBook': exerciseBookName,
        'language': obj.language,
        'searchSource': obj.searchSource,
        'definitionSources': obj.definitionSources.split(","),
    }
        
    return data

#####################################################
# Exported functions
#####################################################
# Return:
# {words : [], source1 : [], source2 : [], ...}
def searchWords(word, source, language, limits = 10):
    candidates = ecdict.match(word,10000)
    words = [i[0] for i in candidates]
    collins_score = [-1 if i[1] is None else i[1] for i in candidates]
    oxford_score = [-1 if i[2] is None else i[2]*5 for i in candidates]
    frq_score = [-1 if i[3] is None or i[3]==0 else i[3]/1000000 for i in candidates]
    #translation = [i[4] for i in candidates]
    
    score = collins_score+oxford_score+frq_score
    words1 = [x for _, x in sorted(zip(score, words), reverse=True)]
    words2 = words1[:limits]
    if len(words)==0 or words2[0]!=word:
        words2.insert(0,word)
    
    return queryWordsDefinitions(words2, language = language, sources = [source])


## Get the words definitions
## Format:
## {words : [], source1 : [], source2 : [], ...}
def queryWordsDefinitions(words, language, sources):
    if not isinstance(sources,list):
        sources = [sources]
    words = [word.lower() for word in words]
    data={'words':[]}
    for key in sources:
        data[key] = []
    
    for word in words:
        res = queryWordDefinitions(word, language, sources)
        data['words'].append(word)
        for key in sources:
            data[key].append(res[key])
    return data
    
## Return:
## {source1 : defintion, source2: definition, ...}
def queryWordDefinitions(word, language, sources):
    if not isinstance(sources,list):
        sources = [sources]
    updateWordDatabase(word, language, sources)
    data =  {source: formatWordDefinition(word, language = language, source=source ) for source in sources}
    return data

# Get the soundmarks for a word
# Return:
# {region1: soundMark, region2: soundmark}
def getSoundmarks(word, regions):
    word = word.lower()
    data = {region: formatSoundmark(word, region) for region in regions}
    data = removeNoneItems(data)
    return data


def getPronounce(word, region, encode=True):
    data=loadPronounce(word, region)
    if encode:
        return base64.b64encode(data).decode()
    else:
        return data
    
def updateWordAnnotation(user, word, type, data):
    if data=="":
        if existsWordAnnotationDB(user, word, type):
            deleteWordAnnotationDB(user, word, type)
    else:
        updataWordAnnotationDB(user, word, type, data)

def getWordAnnotation(user, word, type):
    if existsWordAnnotationDB(user, word, type):
        return getWordAnnotationDB(user, word, type)
    else:
        return ""

##########################
# Glossary words
##########################
def addGlossaryWord(user, bookName, word):
    addGlossaryBook(user, bookName)
    if not existGlossaryWord(user, bookName, word):
        addGlossaryWordDB(user, bookName, word)


def queryGlossaryWords(user, bookName, language, source):
    if not existGlossaryBook(user, bookName):
        return []
    words,addDates = getGlossaryWordsAndDates(user, bookName)
    
    data = queryWordsDefinitions(words, language=language, sources = [source])
    data['addDates'] = addDates
    return data

# Return:
# {words: [], source: [], addDates: []}
def getGlossaryWordsAndDates(user, bookName):
    if not existGlossaryBook(user, bookName):
        return []
    objs = getGlossaryWordsDB(user, bookName)
    words = [i.word for i in objs]
    addDates = [i.addDate for i in objs]
    return words,addDates

def deleteGlossaryWord(user,bookName, word):
    addUserInfo(user, bookName)
    userObj = getUserInfoDB(user)
    if userObj.glossaryBook!=None and userObj.glossaryBook.bookName==bookName:
        books = getGlossaryBooks(user)
        books = [x for x in books if x!=bookName]
        if len(books)!=0:
            setDefaultGlossaryBook(user, books[0])
    deleteGlossaryWordDB(user, bookName, word)

def existGlossaryWord(user, bookName, word):
    return existsGlossaryWordDB(user, bookName, word)
        

##########################
# Glossary book
##########################
def addGlossaryBook(user, bookName):
    addUserInfo(user, bookName)
    if not existGlossaryBook(user, bookName):
        addGlossaryBookDB(user, bookName)

def getGlossaryBooks(user):
    objs = getGlossaryBooksDB(user=user)
    books = [i.bookName for i in objs]
    return books

def deleteGlossaryBook(user, bookName):
    deleteGlossaryBookDB(user, bookName)

def existGlossaryBook(user, bookName):
    return existsGlossaryBookDB(user, bookName)

def setDefaultGlossaryBook(user, bookName):
    if not existsGlossaryBookDB(user, bookName):
        addGlossaryBook(user, bookName)
    obj = getUserInfoDB(user)
    obj.glossaryBook = getGlossaryBookDB(user, bookName)
    obj.save()


def getGlossaryBookFromWord(user, word):
    objs = getGlossaryBooksDB(user)
    bookNames = [obj.bookName for obj in objs]
    exists = [existsGlossaryWordDB(user, name, word) for name in bookNames]
    if any(exists):
        i = exists.index(True)
        return bookNames[i]
    else:
        return None


##########################
# User information
##########################
def addUserInfo(user, bookName = defaultUserValue.glossaryBookName):
    if not existUserInfo(user):
        addUserInfoDB(user, bookName)
        
def getUserInfo(user):
    if user!=None:
        addUserInfo(user, defaultUserValue.glossaryBookName)
        userBooks = getGlossaryBooksDB(user=user)
        if len(userBooks)==0:
            addGlossaryBook(user, defaultUserValue.glossaryBookName)
            userBooks = getGlossaryBooksDB(user=user)
            
        obj = getUserInfoDB(user)
        if obj.glossaryBook==None:
            obj.glossaryBook = userBooks[0]
            obj.save()
        if obj.exerciseBook==None:
            obj.exerciseBook = userBooks[0]
            obj.save()
    return formatUserInfo(user)

def existUserInfo(user):
    return existUserInfoDB(user)


##########################
# Exercise hub
##########################
def setExerciseBook(user, bookName):
    addGlossaryBook(user, bookName)
    obj = getUserInfoDB(user)
    obj.exerciseBook = getGlossaryBookDB(user, bookName)
    obj.save()
    
def getExerciseBookInformation(user, bookName):
    addGlossaryBook(user, bookName)
    allWords, _ = getGlossaryWordsAndDates(user, bookName)
    learningWordObjs = getExerciseHistoryDB(user).filter(word__in = allWords)
    learningWord = [x['word'] for x in learningWordObjs.order_by('word').values('word').distinct()]
    data={
        'learning':len(learningWord),
        'not learned': len(allWords) - len(learningWord),
        'total': len(allWords)
    }
    return data
    

##########################
# Exercise
##########################

# Return:
# {words : [], source : []}
def queryNextExerciseWords(user, bookName, language, source, n=2):
    allWords, _ = getGlossaryWordsAndDates(user, bookName)
    learningWordObjs = getExerciseHistoryDB(user).filter(word__in = allWords)
    learningWordsMat = list(learningWordObjs.values_list('word','date', 'studyTime','answer'))
    if len(learningWordsMat)>0:
        learningWordsDF = pd.DataFrame(learningWordsMat)
        learningWordsDF.columns = ['word', 'date', 'studyTime', 'answer']
    else:
        learningWordsDF = pd.DataFrame({'word':[], 'date':[], 'studyTime':[], 'answer':[]})
    prediction = predictNextWordsLogistic(allWords, learningWordsDF, n=n)
    
    # Query definition
    data = queryWordsDefinitions(prediction.word, language = language, sources = source)
    data[source] = [definition if definition != None \
        else queryWordDefinitions(word, language = language, sources = Source.google)[Source.google][0] \
            for word, definition in zip(prediction.word,data[source])]
    
    # Query custom definition
    customDefinition = [getWordAnnotation(user, word, Annotation.definition) for word in prediction.word]
    data["customDefinition"] = customDefinition
    
    # Query custom definition
    note = [getWordAnnotation(user, word, Annotation.note) for word in prediction.word]
    data["note"] = note
    
    # Query soundmarks
    soundmarks = [getSoundmarks(word, ['US', 'UK']) for word in prediction.word]
    US = [s['US'] if 'US' in s else None for s in soundmarks]
    UK = [s['UK'] if 'UK' in s else None for s in soundmarks]
    data['US'] = US
    data['UK'] = UK
    
    # probability of remembering it
    data['probs'] = [None if math.isnan(x) else x for x in prediction.prob]
    data['ids'] = [str(uuid.uuid1()) for x in prediction.word]
    
    return data
    

def addOrUpdateExerciseAnswer(user, bookName,id, word, date, answer, studyTime):
    ## Time since unix time
    date = parse(date).timestamp()
    if studyTime==0:
        studyTime=1
    return addOrUpdateExerciseWordDB(user, bookName,id, word, date, answer, studyTime)
