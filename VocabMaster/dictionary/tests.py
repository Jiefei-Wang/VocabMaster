from django.test import TestCase
from VocabMaster.dictionary.dictionaries import *
from VocabMaster.dictionary.models import *
from VocabMaster.dictionary.dictionary_api import *
from VocabMaster.dictionary.pronunciation import *
from VocabMaster.utils.constants import *


# Create your tests here.
class DictTestCase(TestCase):
    searchSources = [Dictionaries.google, Dictionaries.dictionaryapi]
    needSync = [Dictionaries.google, Dictionaries.dictionaryapi]
    def test_dict_from_EN(self):
        word = 'hello'
        word2 = "apple"
        for dict in self.searchSources:
            ## exist function
            self.assertEqual(
                Dict.existsWithoutSync(dict, word, Language.en, Language.zh), 
                dict not in self.needSync)

            Dict.getWordMeaning(dict, word, Language.en, Language.zh)

            self.assertEqual(Dict.existsWithoutSync(dict, word, Language.en, Language.zh), True)
            
            ## exist function
            self.assertEqual(Dict.exists(dict, word2, Language.en, Language.zh), True)
    
    def test_sync_database(self):
        word = 'peach'
        Dict.syncDatabase(Dictionaries.google, word, Language.en, Language.zh)
        self.assertEqual(Dict.existsWithoutSync(Dictionaries.google, word, Language.en, Language.zh), True)


def APITestCase(TestCase):
    searchSources = [Dictionaries.google, Dictionaries.ecdict, Dictionaries.dictionaryapi]
    def test_searchWords(self):
        word = "test"
        primaryLanguage = Language.zh
        displayLanguage = Language.zh
        res = searchWords(word, self.searchSources, primaryLanguage, displayLanguage)
        self.assertTrue(len(res.words) > 0)
        self.assertTrue(len(res.words) == len(res.definitions))
    
    def test_getWordMeaning(self):
        word = "test"
        primaryLanguage = Language.zh
        displayLanguage = Language.zh
        res = getWordDefinition(word, self.searchSources, primaryLanguage, displayLanguage)
        self.assertTrue(len(res.words) > 0)
        self.assertTrue(len(res.words) == len(res.definitions))


class PronounciationTestCase(TestCase):
    def test_getSoundmarks(self):
        word = "foot"
        res = Pronounciation.getSoundmarks(word)
        self.assertTrue(len(res) > 0)
    
    def test_getPronounce(self):
        word = "teeth"
        region = "UK"
        res = Pronounciation.getPronounce(word, region)
        self.assertTrue(len(res) > 0)

        word = "length"
        region = "US"
        res = Pronounciation.getPronounce(word, region)
        self.assertTrue(len(res) > 0)

        
        word = "length"
        region = "TTT"
        self.assertRaises(Exception, Pronounciation.getPronounce, word, region)

