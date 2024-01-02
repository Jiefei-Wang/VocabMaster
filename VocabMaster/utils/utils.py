import langid
import logging

from .constants import Language
## Detech the language used in text
## Input:
## text: string
## language: string, the language to be detected beside english
def detect_lang(text, language):
    # unique
    if language == Language.en:
        return Language.en
    langid.set_languages(['en', language])
    lang = langid.classify(text)
    return lang[0]


logger = logging.getLogger("mylogger")

