"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.views.generic import RedirectView

# API viewset
from rest_framework import routers
from beer import views
# from register import views
# from django.views.generic import ProductView

# class HomeTemplateView(ProductView):
#     template_name = 'index.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('/', include('beer.urls')),
    path('', RedirectView.as_view(url="/home", permanent=True)),
    path('user/', include('user.urls')),
    # path('', include('register.urls')),
    # path('', HomeTemplateView.as_view(), name='home'),
]
