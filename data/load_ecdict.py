import sys
import os
import django

sys.path.append('./')
os.environ['DJANGO_SETTINGS_MODULE'] = 'english.settings'
django.setup()

import pickle
from api.models import Ecdict
with open('dictionary\ecdict.pkl', 'rb') as f:
    # Deserialize the object from the file
    records = pickle.load(f)

## batch add words
bulk_list = []
for i in range(len(records)):
    if i//1000 == i/1000:
        print(f"{i}/{len(records)}")
    record = records[i]
    word = record[0]
    translation = record[1]
    if translation==None:
        next
    collins = record[2]
    if collins == None:
        collins = -1
    oxford = record[3]
    if oxford == None:
        oxford = -1
    frq = record[4]
    if frq == None:
        frq = -1
    bulk_list.append(Ecdict(
        word=word,
        meanings = translation,
        collins = collins,
        oxford = oxford,
        frequency = frq))

## detele the existing data
Ecdict.objects.all().delete()
## insert new records
bulk_msj = Ecdict.objects.bulk_create(bulk_list)
