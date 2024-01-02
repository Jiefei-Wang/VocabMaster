from django.db import models
from ..utils.models import TimeStampedModel

# Create your models here.
class WordDefinition(TimeStampedModel):
    word = models.CharField(max_length=1000)
    source = models.CharField(max_length=100)
    fromLanguage = models.CharField(max_length=10)
    toLanguage = models.CharField(max_length=10)
    meanings = models.TextField()
    
    def __str__(self):
        return f'{self.source}({self.modified}): {self.word}\n{self.meanings}'
    
    class Meta:
        indexes = [
            models.Index(fields=['word'], name='WordDefinition_word_idx'),
            models.Index(fields=['source','word'], name='WordDefinition_source_word'),
        ]
        ## unique together
        constraints = [
            models.UniqueConstraint(fields=['word','source','fromLanguage','toLanguage'], name='WordDefinition_unique'),
        ]

class WordScore(models.Model):
    word = models.CharField(max_length=1000)
    collins = models.FloatField()
    oxford = models.FloatField()
    frequency = models.FloatField()
    score = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['word', 'score'], name='WordScore_word_score'),
        ]
        ordering = ['-score']



class WordPronounce(models.Model):
    word = models.CharField(max_length=1000)
    source = models.CharField(max_length=100)
    region = models.CharField(max_length=100, null=True)
    soundmark = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f'{self.word} -- source: {self.source} region: {self.region} soundmark: {self.soundmark}'
    class Meta:
        indexes = [
            models.Index(fields=['word'], name='WordPronounce_word_idx'),
        ]