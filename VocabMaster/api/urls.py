from django.urls import path
from . import views

urlpatterns = [
    path('jsonApi', views.jsonApi),
    path('<slug:word>', views.index),
    path('<slug:word>/', views.index),
    path('pronounce/<slug:region>/<slug:word>', views.pronounce),
    path('history', views.History),
]
