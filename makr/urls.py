from django.urls import path, include

from makr import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.result, name='result')

]