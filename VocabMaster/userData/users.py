from .models import UserInfo, GlossaryBooks
from ..utils.utils import logger
# username = "jiefei"
# User.get(username)
# User.exists(username)
# User.add(username)
class User:
    @classmethod
    def exists(cls, username):
        return UserInfo.exists(username)

    @classmethod
    def get(cls, username):
        if not UserInfo.exists(username):
            logger.error("User %s does not exist", username)
            return
        if UserInfo.exists(username):
            obj = UserInfo.get(username)
            data = obj.toDict()
        return data
    
    @classmethod
    def update(cls, username, args):
        if not UserInfo.exists(username):
            logger.error("User %s does not exist", username)
            return
        if 'glossaryBook' in args:
            cls._addBookIfNotExist(username, args['glossaryBook'])
        if 'exerciseBook' in args:
            cls._addBookIfNotExist(username, args['exerciseBook'])
        UserInfo.update(username, args)
    @classmethod
    def add(cls, username, args = {}):
        if UserInfo.exists(username):
            logger.error("User %s exists", username)
            return
        
        values = UserInfo.getTemplate()
        for i in args:
            values[i] = args[i]

        cls._addBookIfNotExist(username, values['glossaryBook'])
        cls._addBookIfNotExist(username, values['exerciseBook'])
        UserInfo.add(username, values=values)

    def _addBookIfNotExist(user, bookName):
        if not GlossaryBooks.exists(user, bookName):
            GlossaryBooks.add(user, bookName)
        