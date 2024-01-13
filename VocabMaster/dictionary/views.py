from django.shortcuts import render
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest,HttpResponseForbidden

import json


from .dictionary_api import getWordDefinition, searchWords
from .pronunciation import Pronounciation
from ..utils.utils import detect_lang, logger,Language
from ..utils.api_utils import jsonPreprocess
# Create your views here.




def getWordTranslationInfo(userInfo, word):
    searchSources = userInfo['searchSources']
    primaryLanguage = userInfo['primaryLanguage']
    displayLanguage = userInfo['displayLanguage']
    fromLanguage = detect_lang(word, primaryLanguage)
    if fromLanguage == Language.en:
        toLanguage = displayLanguage
    else:
        toLanguage = Language.en
    
    return searchSources, fromLanguage, toLanguage

## Search a single word
## input: 
## word: the word to search
## output:
## data: a dictionary containing the search result
## data['searchedWord']: the word to search
## data['words']: a list of words as the search result
## data['definitions']: a list of definitions corresponding to the words
def searchApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)
    word = body['word']
    sources, fromLanguage, toLanguage = getWordTranslationInfo(userInfo, word)
    data = searchWords(word, sources, fromLanguage, toLanguage, limits=100)
    data['searchedWord'] = word
    logger.info(f'Search API returns Data: {data.keys()}')
    return JsonResponse(data)

def wordDefinitionApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)
    word = body['word']
    sources, fromLanguage, toLanguage = getWordTranslationInfo(userInfo, word)
    data = getWordDefinition(word, sources, fromLanguage, toLanguage)
    data['searchedWord'] = word
    logger.info(f'wordDefinition API returns Data: {data.keys()}')
    return JsonResponse(data)


def getSoundmarksApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)

    word = body['word']
    data = {}
    data['word'] = word
    data['regions'] = Pronounciation.regions
    soundmarks = Pronounciation.getSoundmarks(word)
    for region in Pronounciation.regions:
        if region in soundmarks:
            data[region] = soundmarks[region]
        else:
            data[region] = ''

    logger.info(f'getSoundmarks API returns Data: {data.keys()}')
    return JsonResponse(data)


def getPronounceApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)

    word = body['word']
    region = body['region']
    data = {}
    data['word'] = word
    data['data'] = Pronounciation.getPronounce(word, region)
    logger.info(f'getPronounce API returns Data: {word} + {region}')
    return JsonResponse(data)


