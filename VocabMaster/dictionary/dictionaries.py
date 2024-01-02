from datetime import datetime
from django.utils import timezone

from .models import *
from ..utils.utils import logger
from ..utils.constants import searchableDict

class Dict:
    updateIntervalDays = 30
    name = None

    ## Get the definition of a list of words
    ## Return: defintion of the words
    @classmethod
    def getWordMeaning(cls, source, word, fromLanguage, toLanguage):
        dict = Dictionaries[source]
        dict.syncDatabase(source, word, fromLanguage, toLanguage)
        res = dict.getWordMeaningWithoutSync(source, word, fromLanguage, toLanguage)
        return res

    ## Internal function, should not be called directly
    @classmethod
    def getWordMeaningWithoutSync(cls, source, word, fromLanguage, toLanguage):
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
        dict.syncDatabase(source, word, fromLanguage, toLanguage)
        res = dict.existsWithoutSync(source, word, fromLanguage, toLanguage)
        return res

    @classmethod
    def existsWithoutSync(cls, source, word, fromLanguage, toLanguage):
        res = WordDefinition.objects.filter(
            word=word,
            source=source,
            fromLanguage=fromLanguage,
            toLanguage=toLanguage).exists()

        return res
    
    @classmethod
    def syncDatabase(cls, source, word, fromLanguage, toLanguage):
        existInDB = cls.existsWithoutSync(source, word, fromLanguage, toLanguage)
        if existInDB:
            lastUpdateTimes = cls.getUpdateTime(source, word, fromLanguage, toLanguage)
            dayDiffs = (timezone.now() - lastUpdateTimes).days
            if dayDiffs > cls.updateIntervalDays:
                cls._syncDatabase(word, fromLanguage, toLanguage)
        else:
            cls._syncDatabase(word, fromLanguage, toLanguage)
        
        
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
            ## It will use network
            import translators.server as tss
            if fromLanguage==toLanguage:
                meaning = word
            else:
                meaning = tss.google(word, from_language=fromLanguage, to_language=toLanguage)
            cls.addOrCreate(cls.name, word, fromLanguage, toLanguage, meaning)
        except  Exception as e:
            logger.error(f'Google translation failed for {word}. Error: {e}')
    
# fromLanguage = Language.en
# toLanguage = Language.zh
# word = "test"
# word = "测试"
# Ecdict.get("test", "en", "zh")
# Google.get("test", "en", "zh")

Dictionaries = searchableDict({cls.name:cls for cls in Dict.__subclasses__()})

