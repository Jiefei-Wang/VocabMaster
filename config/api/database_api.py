from .models import *
import datetime
from .keys import *

#####################################################
# Utilities
#####################################################

#####################################################
# ecdict
#####################################################
def existECWordDB(word):
    return Ecdict.objects.filter(word=word).exists()
def allECwordsDB():
    return Ecdict.objects.values_list('word', flat=True)


#####################################################
# Database operation
#####################################################

# Dictionary missing word
def existMissingWordDB(word, language, source):
    return MissingWord.objects.filter(word=word, language=language, source=source).exists()

def getMissingWordDB(word, language, source):
    return MissingWord.objects.get(word=word, language=language, source=source)

def existsWordDB(word, language, source=None):
    filter = WordDefinition.objects.filter(word=word, language=language)
    if source != None:
        filter=filter.filter(source=source)
    return filter.exists()

def getWordsDB(word, language, source=None):
    filter = WordDefinition.objects.filter(word=word, language=language)
    if source != None:
        filter=filter.filter(source=source)
    return filter
        
def markMissingDB(word, language, source):
    obj, created = MissingWord.objects.update_or_create(word=word, language=language, source=source)
    obj.lastUpdate = datetime.datetime.now(tz=datetime.timezone.utc)
    obj.save()

def saveWordDB(source, word, language, meanings):
    obj, created = WordDefinition.objects.get_or_create(source = source, word=word, language=language)
    obj.meanings = meanings
    obj.save()

def existsPronounceDB(word, source=None, region=None):
    filter=WordPronounce.objects.filter(word=word)
    if source!=None:
        filter = filter.filter(source=source)
    if region!=None:
        filter = filter.filter(region=region)
    return filter.exists()

def getPronouncesDB(word, source=None, region=None):
    filter=WordPronounce.objects.filter(word=word)
    if source!=None:
        filter = filter.filter(source=source)
    if region!=None:
        filter = filter.filter(region=region)
    if source!=None and region!=None:
        return filter.get()
    return filter

def savePronounceDB(word, region, soundmark):
    obj, created = WordPronounce.objects.get_or_create(word=word, 
                                                       region=region,
                                                       soundmark = soundmark)
    obj.save()



## Word customization
def existsWordAnnotationDB(user, word, type):
    filter=WordAnnotation.objects.filter(user=user, word=word,type=type)
    return filter.exists()

def getWordAnnotationDB(user, word, type):
    return WordAnnotation.objects.get(user=user, word=word,type=type)
    
def updataWordAnnotationDB(user, word, type, data):
    obj, created = WordAnnotation.objects.update_or_create(user=user, word=word,type=type)
    obj.data = data
    obj.save()

def deleteWordAnnotationDB(user, word, type):
    getWordAnnotationDB(user=user, word=word,type=type).delete()
    


## Glossary book
def existsGlossaryBookDB(user, bookName):
    return GlossaryBooks.objects.filter(user=user,bookName=bookName).exists()

def addGlossaryBookDB(user, bookName):
    if not existsGlossaryBookDB(user, bookName):
        obj = GlossaryBooks.objects.create(user=user,bookName=bookName)

def getGlossaryBooksDB(user):
    return  GlossaryBooks.objects.filter(user=user)

def getGlossaryBookDB(user, bookName):
    return  GlossaryBooks.objects.filter(user=user, bookName=bookName).get()

def deleteGlossaryBookDB(user, bookName):
    getGlossaryBookDB(user=user, bookName=bookName).delete()
    
## Glossary words
def existsGlossaryWordDB(user, bookName, word):
    book = getGlossaryBookDB(user, bookName)
    return GlossaryWords.objects.filter(book=book,word=word).exists()

def addGlossaryWordDB(user, bookName, word):
    book = getGlossaryBookDB(user=user, bookName=bookName)
    if not existsGlossaryWordDB(user, bookName, word):
        obj = GlossaryWords.objects.create(
            book=book,
            word=word, 
            addDate=datetime.datetime.now(tz=datetime.timezone.utc)
        )

def getGlossaryWordDB(user, bookName, word):
    book = getGlossaryBookDB(user, bookName)
    return GlossaryWords.objects.get(book=book,word=word)

def getGlossaryWordsDB(user, bookName):
    book = getGlossaryBookDB(user, bookName)
    return GlossaryWords.objects.filter(book=book)

def deleteGlossaryWordDB(user, bookName, word):
    getGlossaryWordDB(user=user, bookName=bookName, word=word).delete()
    
    

## User default
def existUserInfoDB(user):
    return UserInfo.objects.filter(user=user).exists()

def getUserInfoDB(user):
    return UserInfo.objects.get(user=user)

def addUserInfoDB(user, glossaryBook = defaultUserValue.glossaryBookName,\
    exerciseBook = defaultUserValue.exerciseBook,\
    language = defaultUserValue.language,\
    searchSource=defaultUserValue.searchSource,\
    definitionSources=defaultUserValue.definitionSources):
    
    addGlossaryBookDB(user, glossaryBook)
    addGlossaryBookDB(user, exerciseBook)
    glossaryBookObj = getGlossaryBookDB(user, glossaryBook)
    exerciseBookObj = getGlossaryBookDB(user, exerciseBook)
    UserInfo.objects.create(user=user, 
        glossaryBook=glossaryBookObj, 
        exerciseBook=exerciseBookObj,
        language=language,
        searchSource=searchSource,definitionSources=definitionSources)
    
    

## Exercise history
def addOrUpdateExerciseWordDB(user, bookName, id, word, date, answer, studyTime):
    obj, created = History.objects.get_or_create(
        uuid=id,
        defaults={
            'user':user,
            'bookName':bookName,
            'word':word,
            'date':date,
            'studyTime':studyTime,
            'answer': answer
        }
        )
    if not created:
        obj.answer = answer
        obj.save()
    

def getExerciseHistoryDB(user):
    return History.objects.filter(user = user)
