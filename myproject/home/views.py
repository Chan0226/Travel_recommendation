from django.shortcuts import render
from user.models import User
from django.http import HttpResponse


def hello(request):
    text = {}

    login_session = request.session.get('login_session', '')

    if login_session == '':
        text['login_session'] = False
    else:
        text['login_session'] = True

    return render(request, 'home/index.html', text)
