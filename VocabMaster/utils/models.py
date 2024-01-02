from django.db import models

# Create your models here.
## A base class for recording the time of creation and modification of an object
class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    modified = models.DateTimeField(auto_now = True)
    
    class Meta:
        abstract = True