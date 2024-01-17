from django.shortcuts import render
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest,HttpResponseForbidden

from .models import UserDefinedWordData
from ..utils.utils import logger
from ..utils.api_utils import jsonPreprocess


# Create your views here.
def getUserDefinedDataApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)
    user = userInfo['user']
    word = body['word']
    type = body['type']

    query = UserDefinedWordData.filter(userInfo['user'], type, word)
    if UserDefinedWordData.exists(user, type, word):
        userData = UserDefinedWordData.filter(user, type, word).first().data
    else:
        userData = ''
    
    data = {}
    data['word'] = word
    data['data'] = userData

    logger.info(f'UserDefinedData get API: {user} -- {type} -- {word}')
    return JsonResponse(data)



def setUserDefinedDataApi(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Only POST request is allowed")
    body, userInfo = jsonPreprocess(request)
    user = userInfo['user']
    word = body['word']
    type = body['type']
    data = body['data']
    if not UserDefinedWordData.exists(user, type, word):
        UserDefinedWordData.add(user, type, word, data)
    else:
        UserDefinedWordData.filter(user, type, word).update(data=data)
    logger.info(f'UserDefinedData set API: {user} -- {type} -- {word}')
    
    return HttpResponse("OK")

