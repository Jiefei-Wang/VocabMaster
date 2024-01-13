
## This file contains the JSON API for the dictionary
## All requests will be directed to a function in this file

## pronounciation
from gtts import gTTS

from django.db.models.functions import Length

# from VocabMaster.dictionary.models import *
from .models import *
from .dictionaries import Dictionaries
from ..utils.utils import detect_lang
from ..utils.constants import Language


## Return a list of words
def getEngWordsList(word, limits = 10):
    candidates = WordScore.objects.filter(word__istartswith=word).order_by("-score")[:limits]
    words = [i.word for i in candidates]
    return words

## Return a list of words
def getNonEngWordsList(word, searchSources, limits = 10):
    words = set()
    for source in searchSources:
        candidates = WordDefinition.objects.filter(word__istartswith=word, source = source).order_by(Length('word').asc())[:limits]
        words = words.union(set([i.word for i in candidates]))
        if len(words)>=limits:
            break
    ## sort the words by length
    words = sorted(list(words), key=len)[:limits]
    return words

## search words from database and return the definitions
## of the matched words
# Return:
# {words : [...], definitions : [...]}
def searchWords(word, sources, fromLanguage, toLanguage, limits = 10):
    ## Cases:
    ## word is English: to search language
    ## word is non-English: to English
    ##模糊搜索django数据库
    if fromLanguage == Language.en:
        words = getEngWordsList(word, limits)
    else:
        words = getNonEngWordsList(word, sources, limits)
    
    ## query the definitions from the dictionary ordered by the searchSources
    ## if the word can be found in multiple dictionaries, use the first one
    wordsDefinitions = {word: None for word in words}
    remainingWords = set(words)
    for source in sources:
        sourceDict = Dictionaries[source]

        result = [sourceDict.getWordMeaning(source, word, fromLanguage, toLanguage) for word in remainingWords]
        
        resultDict = {word: definition for word, definition in zip(remainingWords, result) if definition!=None}

        wordsDefinitions.update(resultDict)
        remainingWords = remainingWords - set(resultDict.keys())
    
    ## make sure the order is the same as the input
    ## remove the None value
    words = [word for word in words if wordsDefinitions[word]!=None]
    definitions = [wordsDefinitions[i] for i in words]

    ## add the word to the database if not exist
    if not word in words:
        words.insert(0,word)
        words = words[:limits]
        definitions.insert(0, "Click to see details")
        definitions = definitions[:limits]

    return {'words': words, 'definitions': definitions}




## given a word, return its definition from different sources
## Return: {sources: [...], definitions: [...]}
def getWordDefinition(word, sources, fromLanguage, toLanguage):
    definitions = []
    for source in sources:
        sourceDict = Dictionaries[source]
        definition = sourceDict.getWordMeaning(source, word, fromLanguage, toLanguage)
        definitions.append(definition)
    ## remove None in sources
    sources = [source for source, definition in zip(sources, definitions) if definition!=None]
    definitions = [definition for definition in definitions if definition!=None]
    return {'sources': sources, 'definitions': definitions}
    





