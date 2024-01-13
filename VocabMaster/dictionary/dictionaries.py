## This file provides an intermediate layer between the database and the dictionary API

import requests
import translators.server as tss

from datetime import datetime
from django.utils import timezone

from .models import *
from ..utils.utils import logger
from ..utils.constants import searchableDict, Language


class Dict:
    updateIntervalDays = 30
    name = None

    ## Get the definition of a list of words
    ## Return: defintion of the words
    ## if the word is not found, return None
    @classmethod
    def getWordMeaning(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        dict.syncDatabase(source, word, fromLanguage, toLanguage)
        res = dict.getWordMeaningWithoutSync(source, word, fromLanguage, toLanguage)
        return res

    ## Internal function, should not be called directly
    @classmethod
    def getWordMeaningWithoutSync(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        objs = WordDefinition.objects.filter(
            word=word, 
            source=source, 
            fromLanguage=fromLanguage, 
            toLanguage=toLanguage)
        if objs.exists():
            return objs.first().meanings
        else:
            return None
    
    @classmethod
    def getUpdateTime(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        objs = WordDefinition.objects.filter(
            word=word,
            source=source,
            fromLanguage=fromLanguage,
            toLanguage=toLanguage)
        
        if objs.exists():
            return objs.first().modified
        else:
            return None

    @classmethod
    def addOrCreate(cls, source, word, fromLanguage, toLanguage, meanings):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        obj, created = WordDefinition.objects.get_or_create(
            word=word,
            source=source,
            fromLanguage=fromLanguage,
            toLanguage=toLanguage)
        obj.meanings = meanings
        obj.save()
    
    @classmethod
    def exists(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        dict.syncDatabase(source, word, fromLanguage, toLanguage)
        res = dict.existsWithoutSync(source, word, fromLanguage, toLanguage)
        return res

    @classmethod
    def existsWithoutSync(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        res = WordDefinition.objects.filter(
            word=word,
            source=source,
            fromLanguage=fromLanguage,
            toLanguage=toLanguage).exists()

        return res
    
    @classmethod
    def syncDatabase(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        word = dict.formatWord(word)
        existInDB = dict.existsWithoutSync(source, word, fromLanguage, toLanguage)
        if existInDB:
            lastUpdateTimes = dict.getUpdateTime(source, word, fromLanguage, toLanguage)
            dayDiffs = (timezone.now() - lastUpdateTimes).days
            if dayDiffs > dict.updateIntervalDays:
                dict._syncDatabase(word, fromLanguage, toLanguage)
        else:
            dict._syncDatabase(word, fromLanguage, toLanguage)
    
    @classmethod
    def formatWord(cls, word):
        return word

    @classmethod
    def _syncDatabase(cls, word, fromLanguage, toLanguage):
        pass



class Ecdict(Dict):
    name = "ecdict"

class Google(Dict):
    name = "google"
    @classmethod
    def _syncDatabase(cls, word, fromLanguage, toLanguage):
        try: 
            if fromLanguage==toLanguage:
                return
            
            meaning = tss.google(word, from_language=fromLanguage, to_language=toLanguage)
            obj = cls.addOrCreate(cls.name, word, fromLanguage, toLanguage, meaning)
            return obj
        except  Exception as e:
            logger.error(f'Google translation failed for {word}. Error: {e}')
        



class Dictionaryapi(Dict):
    name = "dictionaryapi"
    @classmethod
    def _syncDatabase(cls, word, fromLanguage, toLanguage):
        if fromLanguage != "en":
            return
        
        ## Request word data
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
        try:
            response = requests.get(url)
        except Exception:
            print(Exception)
            return
        
        if response.status_code==404:
            return
        else:
            if response.status_code!=200:
                raise Exception(f"Error, word: {word} status code: {response.status_code}")
        
        json_response = response.json()[0]
        meanings = {}
        for x in json_response['meanings']:
            partOfSpeech = x['partOfSpeech']
            definitions = [i['definition'] for i in x['definitions']]
            syn = [j for i in x['definitions'] for j in i['synonyms']]
            ant = [j for i in x['definitions'] for j in i['antonyms']]
            meanings[partOfSpeech] = definitions
        
        meaning = ""
        for key in meanings.keys():
            value = meanings[key]
            text = "\n".join([str(i+1)+ ". " + value[i] for i in range(len(value))])
            meaning += key + ":\n" + text
        
        obj = cls.addOrCreate(cls.name, word, fromLanguage, toLanguage, meaning)

        ## Save pronounce data to database
        soundmarks = [i.get('text', 'none') for i in json_response['phonetics']]
        pronounceUrl = [i.get('audio', 'none') for i in json_response['phonetics']]
        for i in range(len(pronounceUrl)):
            soundmark = soundmarks[i]
            url = pronounceUrl[i]
            if url.endswith('-au.mp3'):
                WordSoundMark(word=word, region="AU", soundmark=soundmark).save()
            if url.endswith('-uk.mp3'):
                WordSoundMark(word=word, region="UK", soundmark=soundmark).save()
            if url.endswith('-us.mp3'):
                WordSoundMark(word=word, region="US", soundmark=soundmark).save()
        
        return obj
    
    @classmethod
    def formatWord(cls, word):
        return word.lower()


# fromLanguage = Language.en
# toLanguage = Language.zh
# word = "test"
# word = "测试"
# Ecdict.get("test", "en", "zh")
# Google.get("test", "en", "zh")

Dictionaries = searchableDict({cls.name:cls for cls in Dict.__subclasses__()})

