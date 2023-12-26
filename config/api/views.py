
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest,HttpResponseForbidden
from django.forms.models import model_to_dict
from django.shortcuts import render

import json 
import time
import json
import logging


from .keys import *
from .models import *
from .query_api import getPronounce,searchWords,\
    updateWordAnnotation,getWordAnnotation,\
    queryWordDefinitions, getSoundmarks,\
    addGlossaryBook, deleteGlossaryBook, getGlossaryBooks, setDefaultGlossaryBook,\
    addGlossaryWord, deleteGlossaryWord, queryGlossaryWords,\
    existGlossaryBook, existGlossaryWord, getGlossaryBookFromWord,\
    setExerciseBook, getExerciseBookInformation, \
    queryNextExerciseWords,\
    addOrUpdateExerciseAnswer,\
    getUserInfo

logger = logging.getLogger("mylogger")
#####################################################
# View
#####################################################

def jsonApi(request):
    #JsonResponse(data)
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    
    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        user = request.user.get_username()
    else:
        user = None
    userInfo = getUserInfo(user)
    searchSource = userInfo['searchSource']
    definitionSources = userInfo['definitionSources']
    language = userInfo['language']
    exerciseBook = userInfo['exerciseBook']
    glossaryBook = userInfo['glossaryBook']
    
    
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print(body)
    action = body['action']
    if 'word' in body:
        word = body['word']
    if 'bookName' in body:
        bookName = body['bookName']
    else:
        bookName=userInfo['glossaryBook']
    if 'target' in body:
        target = body['target']
    else:
        target = None
        
    
    logger.info(f'JSON api GET -- user: {request.user} operation: {body}')
    
    # Return a list of words with their explainations
    if action == "search":
        data = searchWords(word, searchSource, language, limits=100)
        data['searchedWord'] = word
        data['source'] = searchSource
        return JsonResponse(data)
    
    if action == 'queryWordDefinitions':
        data = queryWordDefinitions(word, language, definitionSources)
        data['word'] = word
        data['sources'] = definitionSources
        return JsonResponse(data)
    
    if action == 'queryWordSoundmarks':
        regions = ['US', 'UK']
        data = getSoundmarks(word, regions)
        data['word'] = word
        data['regions'] = regions
        return JsonResponse(data)
    
    ## user info
    if action == 'getUserInfo':
        return JsonResponse(getUserInfo(user))
    
    ## Below require user login
    if not is_authenticated:
        return HttpResponseForbidden('You must log in to perform the action')
    
    if target == "wordAnnotation":
        type = body['type']
        if action == "update":
            data = body['data']
            updateWordAnnotation(user, word, type, data)
        if action == "get":
            data = getWordAnnotation(user, word, type)
        data = {
            "word": word,
            "type": type,
            "data": data
        }
        return JsonResponse(data)
 
    if action == "findBookByWord":
        data = {'book': getGlossaryBookFromWord(user, word)}
        return JsonResponse(data)
    
    if target == 'glossaryWord':
        data = {'action': action,
                'bookName': bookName}
        if action == 'add':
            words = body['words']
            for word in words:
                addGlossaryWord(user, bookName, word)
        if action == 'delete':
            deleteGlossaryWord(user, bookName, word)
        if action == 'query':
            data['words'] = queryGlossaryWords(user, bookName, language, searchSource)
            data['source'] = searchSource
        return JsonResponse(data)
    
    if target == 'glossaryBook':
        data = {'action': action}
        if action == 'get':
            data['books'] = getGlossaryBooks(user)
        if action == 'add':
            addGlossaryBook(user, bookName)
            data['bookName'] = bookName
        if action == 'delete':
            deleteGlossaryBook(user, bookName)
            data['bookName'] = bookName
        if action =='setDefault':
            setDefaultGlossaryBook(user, bookName)
            data['bookName'] = bookName
        return JsonResponse(data)
            
    
    if target == 'exerciseBook':
        data = {'action': action}
        if action == 'get':
            data['bookName'] = exerciseBook
        if action == 'set':
            setExerciseBook(user, bookName)
            data['bookName'] = bookName
        if action == 'showInformation':
            data.update(getExerciseBookInformation(user, bookName))
            data['bookName'] = bookName
        return JsonResponse(data)
        
        
    if target == 'exerciseWords':
        data = {'action': action}
        if action == 'query':
            data['words'] = queryNextExerciseWords(user, bookName, language, searchSource)
            data['source'] = searchSource
        if action == 'addOrUpdate':
            answer = body['answer']
            date = body['date']
            id = body['id']
            studyTime = body['studyTime']
            addOrUpdateExerciseAnswer(user, bookName, id, word, date, answer, studyTime)
        return JsonResponse(data)
        
    if target == 'pronounce':
        if action == 'get':
            region = body['region']
            data = {'data': getPronounce(word,region, encode=True)}
        return JsonResponse(data)
        
    if action == "existGlossary":
        if target == "book":
            data = {'books':existGlossaryBook(user, bookName)}
        if target == "word":
            data = {'books':existGlossaryWord(user, bookName, word)}
        return JsonResponse(data)
    
    return HttpResponseBadRequest(f'The JSON action "{action}" is not allowed')
        


def index(request, word):
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET request is allowed")
        
    data = queryWordDefinitions(word)
    logger.info(f'Word: {word}, Data: {data}')
    return render(request, "api/word.html", {"data":data, "word": word})


def pronounce(request, region, word):
    data = getPronounce(word, region,encode=False)
    
    logger.info(f'Word: {word}')
    if region in data:
        return HttpResponse(data, content_type='audio/mpeg')
    else:
        return HttpResponseNotFound(f'The requested {region} pronounce of {word} is not found. \n'+\
            'Available pronounce:\n '+ ', '.join(data.keys()))

