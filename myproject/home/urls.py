from django.urls import path
from . import views

# http://logalhost/home/
app_name = 'home'
urlpatterns = [path('', views.hello, name='hello')]
