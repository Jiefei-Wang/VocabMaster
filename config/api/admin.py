from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(WordDefinition)
admin.site.register(Ecdict)
admin.site.register(WordAnnotation)
admin.site.register(WordPronounce)
admin.site.register(MissingWord)
admin.site.register(History)
admin.site.register(GlossaryBooks)
admin.site.register(GlossaryWords)
admin.site.register(UserInfo)
