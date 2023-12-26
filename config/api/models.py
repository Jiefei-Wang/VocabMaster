from django.db import models
class WordDefinition(models.Model):
    source = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    ## Translation language when the word is english
    language = models.CharField(max_length=10)
    meanings = models.TextField()
    
    def __str__(self):
        return f'{self.source}: {self.word}\n{self.meanings}'

class Ecdict(models.Model):
    word = models.CharField(max_length=1000, primary_key=True)
    meanings = models.TextField()
    collins = models.IntegerField()
    oxford = models.IntegerField()
    frequency = models.IntegerField()
    
    def __str__(self):
        return f'{self.word}\n{self.meanings}'

class WordAnnotation(models.Model):
    user = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    type = models.CharField(max_length=100)
    data = models.TextField()
    def __str__(self):
        return f'{self.type}: {self.word}\n{self.data}'

class WordPronounce(models.Model):
    word = models.CharField(max_length=1000)
    region = models.CharField(max_length=100, null=True)
    soundmark = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f'{self.word} -- region: {self.region} soundmark: {self.soundmark}'
           
class MissingWord(models.Model):
    word = models.CharField(max_length=1000)
    source = models.CharField(max_length=20)
    language = models.CharField(max_length=10)
    lastUpdate = models.DateTimeField(null=True)
    
    def __str__(self):
        return f'{self.word}: '+ \
            f'Source: {self.source} ({self.lastUpdate})'
     
class GlossaryBooks(models.Model):
    user = models.CharField(max_length=100)
    bookName = models.CharField(max_length=100)

class GlossaryWords(models.Model):
    book = models.ForeignKey(GlossaryBooks, on_delete=models.CASCADE)
    word = models.CharField(max_length=1000)
    addDate = models.DateTimeField()
    
    
class History(models.Model):
    user = models.CharField(max_length=100)
    # Time since 1970-01-01 00:00:00 UTC in seconds
    date = models.BigIntegerField()
    uuid = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    bookName = models.CharField(max_length=100)
    # 0: unknown, 1: fuzzy, 2: known
    answer = models.IntegerField()
    # Time in second
    studyTime = models.IntegerField()
    def __str__(self):
        return f'{self.user}: {self.bookName}:{self.word} -- {self.answer}'

class UserInfo(models.Model):
    user = models.CharField(max_length=100, primary_key=True)
    glossaryBook = models.ForeignKey(GlossaryBooks, on_delete=models.SET_NULL, null=True, related_name='%(class)s_defaultBookName')
    exerciseBook = models.ForeignKey(GlossaryBooks, on_delete=models.SET_NULL, null=True, related_name='%(class)s_exerciseBook')
    language = models.CharField(max_length=10)
    # The source of the definition displayed when searching a word
    searchSource = models.CharField(max_length=100)
    # The sources used in displaying definitions in word details
    definitionSources = models.CharField(max_length=1000)
    
    
    