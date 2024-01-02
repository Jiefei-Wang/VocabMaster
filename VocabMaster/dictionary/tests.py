from django.test import TestCase
from VocabMaster.dictionary.dictionaries import *
from VocabMaster.dictionary.models import *
from VocabMaster.utils.constants import *

# Create your tests here.
class ecdictTestCase(TestCase):
    def test_dict(self):

        ## exist function
        self.assertEqual(Dict.existsWithoutSync(Dictionaries.google, 'test', Language.en, Language.zh), False)

        out = Dict.getWordMeaning(Dictionaries.google, 'test', Language.en, Language.zh)
        self.assertEqual(out, '测试')

        self.assertEqual(Dict.existsWithoutSync(Dictionaries.google, 'test', Language.en, Language.zh), True)
        
        ## filter without update
        out = Dict.getWordMeaningWithoutSync(Dictionaries.google, 'hello', Language.en, Language.zh)
        self.assertEqual(out, None)

        ## exist function
        self.assertEqual(Dict.exists(Dictionaries.google, 'hello', Language.en, Language.zh), True)
