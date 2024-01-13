import json
from ..userData.models import UserInfo

def jsonPreprocess(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    body['user'] = getUserName(request)
    
    userInfo = getUserInfo(body['user'])
    return body, userInfo


def getUserInfo(user):
    if user!=None:
        obj = UserInfo.get(user)
        return obj.toDict()
    else:
        return UserInfo.getTemplate()


def getUserName(request):
    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        user = request.user.get_username()
    else:
        user = None
    return user
