## This python code is used to load the ecdict data into the database
import os
import django
## ranking data
import scipy.stats as ss


## set up django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from VocabMaster.dictionary.models import WordDefinition, WordScore
from VocabMaster.utils.constants import Language
from VocabMaster.dictionary.dictionaries import Dictionaries

## load ecdict data
import pickle
with open('./data/dictionary/ecdict.pkl', 'rb') as f:
    # Deserialize the object from the file
    records = pickle.load(f)

print(f"Total records: {len(records)}")
print(f"First record: {records[0]}")

## get collins, oxford, frequency
collins = [i[2] for i in records]
oxford = [i[3] for i in records]
frq = [i[4] for i in records]

def standardScore(arr):
    arr = [-1 if i is None else i for i in arr]
    return [i/len(arr) for i in ss.rankdata(arr)]

## convert values to standard score
collins = standardScore(collins)
oxford = standardScore(oxford)
frq = standardScore(frq)

## batch add words
bulk_list = []
bulk_list2 = []
for i in range(len(records)):
    if i//1000 == i/1000:
        print(f"{i}/{len(records)}")
    record = records[i]
    word = record[0]
    translation = record[1]
    if translation==None:
        next
    
    bulk_list.append(WordDefinition(
        word=word,
        source = Dictionaries.ecdict,
        fromLanguage = Language.en,
        toLanguage = Language.zh,
        meanings = translation))
    bulk_list2.append(WordScore(
        word = word,
        collins = collins[i],
        oxford = oxford[i],
        frequency = frq[i],
        score = collins[i]+oxford[i]+frq[i] -len(word)/2
    ))



## detele the existing data
WordDefinition.objects.all().delete()
WordScore.objects.all().delete()
## insert new records
bulk_msj = WordDefinition.objects.bulk_create(bulk_list)
bulk_msj2 = WordScore.objects.bulk_create(bulk_list2)
