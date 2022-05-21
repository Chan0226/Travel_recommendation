from django.urls import path
from . import views

app_name = 'beer'
urlpatterns = [
    path('ver2_select', views.ver2_select, name='ver2_select'),
    path('ver2_session', views.ver2_session, name='ver2_session'),
    path('ver2_session', views.cart_add, name='cart_add'),
    path('ver3_select', views.ver3_select, name='ver3_select'),
    path('ver3_session', views.ver3_session, name='ver3_session'),
]
