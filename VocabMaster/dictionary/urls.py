from django.urls import path
from . import views

urlpatterns = [
    path('search', views.searchApi),
    path('wordDefinition', views.wordDefinitionApi),
]


