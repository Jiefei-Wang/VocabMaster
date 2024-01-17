from django.urls import path
from . import views

urlpatterns = [
    path('getUserDefinedData', views.getUserDefinedDataApi),
    path('setUserDefinedData', views.setUserDefinedDataApi),
]


