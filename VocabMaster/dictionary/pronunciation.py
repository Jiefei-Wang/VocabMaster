import base64
import hashlib
import os
import re
import tempfile

from gtts import gTTS

from .dictionaries import Dict, Dictionaries
from ..utils.constants import Language
from .models import WordSoundMark, WordPronounce

# tts = gTTS("test", lang='en', tld='co.uk')

class Pronounciation():
    ## Return: {region: soundmark}
    @classmethod
    def getSoundmarks(cls, word):
        Dict.syncDatabase(Dictionaries.dictionaryapi, word, Language.en, Language.en)
        objs = WordSoundMark.objects.filter(word=word)
        soundmarks = {i.region: i.soundmark for i in objs if i.region in ['UK', 'US']}
        return soundmarks

    
    @classmethod
    def getPronounce(cls, word, region):
        if not WordPronounce.objects.filter(word=word, region=region).exists():
            if region=='UK':
                tts = gTTS(word, lang='en', tld='co.uk')
            elif region=='US':
                tts = gTTS(word, lang='en', tld='com')
            else:
                raise Exception(f'Unrecognized accent: {region}')
            ## create a tempetory file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tts.save(tmp.name)
                data = tmp.read()
            # dataBase64 = base64.b64encode(data).decode()
            WordPronounce.objects.create(word=word, region=region, pronounce=data)

        data = WordPronounce.objects.get(word=word, region=region).pronounce
        return base64.b64encode(data).decode()
    