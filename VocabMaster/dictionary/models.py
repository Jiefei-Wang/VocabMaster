from django.db import models

# Create your models here.
class WordDefinition(models.Model):
    source = models.CharField(max_length=100)
    word = models.CharField(max_length=1000)
    lang_from = models.CharField(max_length=10)
    lang_to = models.CharField(max_length=10)
    meanings = models.TextField()
    
    def __str__(self):
        return f'{self.source}: {self.word}\n{self.meanings}'
