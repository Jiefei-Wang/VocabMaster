from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(GlossaryBooks)
admin.site.register(GlossaryWords)
admin.site.register(History)
admin.site.register(UserInfo)
admin.site.register(UserDefinedWordData)
