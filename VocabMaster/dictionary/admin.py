from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(WordDefinition)
admin.site.register(WordPronounce)
admin.site.register(WordScore)

