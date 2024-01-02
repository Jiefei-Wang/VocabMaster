from django.db import models
from ..utils.models import TimeStampedModel
from ..dictionary.dictionaries import Dictionaries
from ..utils.constants import Language

# Create your models here.


class GlossaryBooks(models.Model):
    user = models.CharField(max_length=100)
    bookName = models.CharField(max_length=100)

    @classmethod
    def add(cls, user, bookName):
        cls.objects.create(user=user, bookName=bookName)

    @classmethod
    def exists(cls, user, bookName):
        return cls.objects.filter(user=user, bookName=bookName).exists()
    
    @classmethod
    def filter(cls, user, bookName = None):
        if bookName is None:
            return cls.objects.filter(user=user)
        else:
            return cls.objects.filter(user=user, bookName=bookName)
    
    @classmethod
    def delete(cls, user, bookName):
        cls.objects.filter(user=user, bookName=bookName).delete()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'bookName'], name='GB_user_bookName')
        ]

class GlossaryWords(TimeStampedModel):
    book = models.ForeignKey(GlossaryBooks, on_delete=models.CASCADE)
    word = models.CharField(max_length=1000)

    @classmethod
    def add(cls, user, bookName, word):
        book = GlossaryBooks.filter(user, bookName)[0]
        cls.objects.create(book=book, word=word)

    @classmethod
    def exists(cls, user, bookName, word):
        book = GlossaryBooks.filter(user, bookName)[0]
        return cls.objects.filter(book=book, word=word).exists()

    @classmethod
    def filter(cls, user, bookName):
        book = GlossaryBooks.filter(user, bookName)[0]
        objs = cls.objects.filter(book=book)
        return objs
    
    @classmethod
    def delete(cls, user, bookName, word = None):
        book = GlossaryBooks.filter(user, bookName)[0]
        if word is None:
            cls.objects.filter(book=book).delete()
        else:
            cls.objects.filter(book=book, word=word).delete()


class UserDefinedWordMeaning(TimeStampedModel):
    user = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    meaning = models.TextField()
    def __str__(self):
        return f'{self.word}:\n{self.meaning}'
    
    @classmethod
    def add(cls, user, word, meaning):
        cls.objects.create(user=user, word=word, meaning=meaning)
    
    @classmethod
    def exists(cls, user, word):
        return cls.objects.filter(user=user, word=word).exists()
    
    @classmethod
    def filter(cls, user, word = None):
        if word is None:
            return cls.objects.filter(user=user)
        else:
            return cls.objects.filter(user=user, word=word)
    
    @classmethod
    def delete(cls, user, word = None):
        if word is None:
            cls.objects.filter(user=user).delete()
        else:
            cls.objects.filter(user=user, word=word).delete()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'word'], name='UDWM_user_word')
        ]

class UserDefinedWordNote(TimeStampedModel):
    user = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    note = models.TextField()
    def __str__(self):
        return f'{self.word}:\n{self.note}'
    
    @classmethod
    def add(cls, user, word, note):
        cls.objects.create(user=user, word=word, note=note)
    
    @classmethod
    def exists(cls, user, word):
        return cls.objects.filter(user=user, word=word).exists()
    
    @classmethod
    def filter(cls, user, word = None):
        if word is None:
            return cls.objects.filter(user=user)
        else:
            return cls.objects.filter(user=user, word=word)
        
    @classmethod
    def delete(cls, user, word = None):
        if word is None:
            cls.objects.filter(user=user).delete()
        else:
            cls.objects.filter(user=user, word=word).delete()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'word'], name='UDWN_user_word')
        ]


class History(TimeStampedModel):
    user = models.CharField(max_length=100)
    uuid = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    bookName = models.CharField(max_length=100)
    # 0: unknown, 1: fuzzy, 2: known
    answer = models.IntegerField()
    def __str__(self):
        return f'{self.user}: {self.bookName}:{self.word} -- {self.answer}'
    
    @classmethod
    def add(cls, user, uuid, word, bookName, answer):
        cls.objects.create(user=user, uuid=uuid, word=word, bookName=bookName, answer=answer)
    
    @classmethod
    def exists(cls, user, word, bookName=None, uuid=None):
        objs = cls.objects.filter(user=user, word=word)
        if bookName is not None:
            objs = objs.filter(bookName=bookName)
        if uuid is not None:
            objs = objs.filter(uuid=uuid)
        return objs.exists()
    
    @classmethod
    def filter(cls, user, word = None, bookName=None, uuid=None):
        objs = cls.objects.filter(user=user)
        if word is not None:
            objs = objs.filter(word=word)
        if bookName is not None:
            objs = objs.filter(bookName=bookName)
        if uuid is not None:
            objs = objs.filter(uuid=uuid)
        return objs
    
    @classmethod
    def delete(cls, user, word, uuid=None):
        objs = cls.objects.filter(user=user, word=word)
        if uuid is not None:
            objs = objs.filter(uuid=uuid)
        objs.delete()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'uuid'], name='History_user_uuid'),
            models.Index(fields=['user', 'created'], name='History_user_created'),
        ]

class UserInfo(models.Model):
    user = models.CharField(max_length=100, primary_key=True)
    glossaryBook = models.CharField(max_length=100)
    exerciseBook = models.CharField(max_length=100)
    ## Determine the search order of the sources
    searchSources = models.CharField(max_length=100)
    ## What is the language displayed in the search results?
    searchLanguage = models.CharField(max_length=10)
    ## What is user's primary language?
    primaryLanguage = models.CharField(max_length=10)
    ## The sources used in displaying definitions in word details
    definitionSources = models.CharField(max_length=1000)
    
    allAttributes = ['user', 'glossaryBook', 'exerciseBook', 'searchSources', 'searchLanguage', 'primaryLanguage', 'definitionSources']
    listAttributes = ['searchSources', 'definitionSources']

    @classmethod
    def exists(cls, username):
        return cls.objects.filter(user=username).exists()
    
    @classmethod
    def get(cls, username):
        return cls.objects.get(user=username)
    
    @classmethod
    def add(cls, username, values):
        values['user'] = username
        for i in cls.listAttributes:
            values[i] = ",".join(values[i])
        cls.objects.create(**values)
    
    @classmethod
    def update(cls, username, values):
        obj = cls.get(username)
        for i in values:
            if i in cls.listAttributes:
                obj.__setattr__(i, ",".join(values[i]))
            else:
                obj.__setattr__(i, values[i])
        obj.save()

    @classmethod
    def delete(cls, username):
        cls.objects.filter(user=username).delete()

    def toDict(self):
        result = {i:self.__getattribute__(i) for i in self.allAttributes}
        for i in self.listAttributes:
            result[i] = result[i].split(",")
        return result
    
    def getTemplate():
        defaultUserValue = {
            'glossaryBook': 'mybook',
            'exerciseBook': 'mybook',
            'searchSources': [Dictionaries.ecdict],
            'primaryLanguage': Language.zh,
            'searchLanguage': Language.zh,
            'definitionSources': [Dictionaries.ecdict, Dictionaries.google]
        }
        return defaultUserValue
