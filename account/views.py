import requests
import json
import datetime
import hashlib
import uuid

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User

#функция, хэширующая пароль
def hash_password( password ):
    #случайное число в шестнадцатиричной сс
    salt = uuid.uuid4().hex
    return hashlib.sha256( salt.encode() + password.encode() ).hexdigest() + ':' + salt


@csrf_exempt
def registration( request ):

    if (request.method != "POST"):
        return JsonResponse (
            {
                'status': False,
                'comment': 'Неподдерживаемый метод запроса'
            }
        )

    #получаем тело запроса
    request_body = json.loads( request.body.decode( 'utf-8' ) )

    user = User.objects.create_user(request_body["name"], request_body["mail"], request_body["password"])
    user.save()

    return JsonResponse( { "status": True } )
