from django.urls import path
from . import views

urlpatterns = [
    path('search', views.searchApi),
    path('wordDefinition', views.wordDefinitionApi),
    path('wordSoundmarks', views.getSoundmarksApi),
    path('wordPronounce', views.getPronounceApi)
]


