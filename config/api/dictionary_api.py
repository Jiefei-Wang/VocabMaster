
import datetime
# handle pronounciation file path
import os
import hashlib
import re

import requests
import langid
## pronounciation
from gtts import gTTS

# Installed from "pip install git+https://github.com/ctoth/PyDictionary.git@remove-goslate#egg=PyDictionary"
#from PyDictionary import PyDictionary

from .keys import *
from .database_api import *

## constrain language
langid.set_languages(['en','zh'])

modelVersion = 1
retryInterval = 3
#####################################################
# Utilities
#####################################################
def detect_lang(word):
    lang = langid.classify(word)
    return lang[0]

def updateWordFromSource(word, language, source, sourceFunc):
    markedMissing = existMissingWordDB(word=word, language=language, source=source)
    if markedMissing:
        obj = getMissingWordDB(word=word, language=language, source=source)
        diff = datetime.datetime.now(tz=datetime.timezone.utc) - obj.lastUpdate
        if diff.seconds/60/60/24 > retryInterval:
            obj.delete()
            markedMissing = False
    
    if not markedMissing:
        exists = existsWordDB(word=word, language=language, source=source)
        if not exists:
            sourceFunc(word, language)

#####################################################
# Exported function
#####################################################
def updateWordDatabase(word, language, sources = allSources):
    nonExistSources = list(set(sources) - set(allSources))
    if len(nonExistSources)>0:
        raise Exception(f'Non exist source found in {sources}')
    
    word = word.lower()
    for source in sources:
        if Dict_list[source].needs_update:
            sourceFunc = globals()[source + "Source"]
            updateWordFromSource(word, 
                                 language=language, 
                                 source=source, 
                                 sourceFunc=sourceFunc)

def loadPronounce(word, region):
    filePath = pronouncePath(word, region)
    # Check if the file exists
    if not os.path.exists(filePath):
        # If the file does not exist, download it
        downloadPronounce(word, region)
        
    # Open the file and return the data
    with open(filePath, 'rb') as file:
        return file.read()
#####################################################
# Search source
#####################################################
def dictionaryapiSource(word, language):    
    word = word.lower()
    if (detect_lang(word) != "en"):
        markMissingDB(word, language=language, source = Source.dictionaryapi)
        return
    
    ## Request word data
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    try:
        response = requests.get(url)
    except Exception:
        print(Exception)
        return
    
    if response.status_code==404:
        markMissingDB(word, language=language, source = Source.dictionaryapi)
        return
    else:
        if response.status_code!=200:
            raise Exception(f"Error, word: {word} status code: {response.status_code}")
    
    json_response = response.json()[0]
    meanings = {}
    synonyms = []
    antonyms = []
    for x in json_response['meanings']:
        partOfSpeech = x['partOfSpeech']
        definitions = [i['definition'] for i in x['definitions']]
        syn = [j for i in x['definitions'] for j in i['synonyms']]
        ant = [j for i in x['definitions'] for j in i['antonyms']]
        meanings[partOfSpeech] = definitions
        synonyms += syn
        antonyms += ant
    
    meaning = ""
    for key in meanings.keys():
        value = meanings[key]
        text = "\n".join([str(i+1)+ ". " + value[i] for i in range(len(value))])
        meaning += key + ":\n" + text
    
    synonyms = ", ".join(synonyms)
    antonyms = ", ".join(antonyms)
    
    ## Save the word data to database
    saveWordDB(Source.dictionaryapi, word, language, meaning)
    
    ## Save pronounce data to database
    soundmarks = [i.get('text', 'none') for i in json_response['phonetics']]
    pronounceUrl = [i.get('audio', 'none') for i in json_response['phonetics']]
    for i in range(len(pronounceUrl)):
        if url.endswith('-uk.mp3'):
            region = "UK"
        elif url.endswith('-us.mp3'):
            region = "US"
        else: next
        savePronounceDB(word, region)
    return True

def googleSource(word, language):
    try: 
        lang = detect_lang(word)
        ## It will use network
        import translators.server as tss
        if (lang == "en"):
            result = tss.google(word, from_language='en', to_language=language.lower())
        else:
            result = tss.google(word, from_language=lang.lower(), to_language='en')
        saveWordDB(Source.google, word, language, result)
    except  Exception as e:
        print(e)

def PyDictionarySource(word, language):
    try:
        dictionary=PyDictionary()
        definitions = dictionary.meaning(word)
        definitionsCombined = ''
        for key, values in definitions.items():
            definitionsCombined = definitionsCombined + key + ':\n'+ '\n'.join([' ' + str(i+1) + '. ' + values[i] for i in range(len(values))])
        saveWordDB(Source.PyDictionary, word, language, definitionsCombined)
    except Exception:
        markMissingDB(word, language=language, source = Source.PyDictionary)

#####################################################
# Pronounciation
#####################################################
def generate_hash(message, length):
  # Encode the message as bytes
  message_bytes = message.encode()
  # Create an MD5 hash object
  hash_obj = hashlib.md5()
  # Update the hash object with the message bytes
  hash_obj.update(message_bytes)
  # Get the hash value as a hexadecimal string
  hash_hex = hash_obj.hexdigest()
  # Return the first 'length' characters of the hex string
  return hash_hex[:length]


def pathSafe(word):
    return re.sub(r'[^a-zA-Z0-9 ]+', '', word) + '_' + generate_hash(word, 10)

def pronouncePath(word, region):
    cwd = os.getcwd()
    file_name = pathSafe(word) + '.mp3'
    file_path = os.path.join(cwd, 'pronunciation', region, file_name)
    return file_path

def downloadPronounce(word, region):
    region=region.upper()
    if region=='UK':
        tts = gTTS(word, lang='en', tld='co.uk')
    elif region=='US':
        tts = gTTS(word, lang='en', tld='com')
    else:
        raise Exception(f'Unrecognized accent: {region}')
    filePath = pronouncePath(word, region)
    dirPath = os.path.dirname(filePath)

    # Create the directories if they do not exist
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
        
    # Save the file
    tts.save(filePath)

