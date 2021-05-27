import requests
import json
import datetime
import hashlib
import uuid

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from django.contrib.auth.models import User
from account.models import *

@csrf_exempt
def registration( request ):
    profile = None

    if (request.method != "POST"):
        return JsonResponse (
            {
                'status': False,
                'comment': 'Неподдерживаемый метод запроса'
            }
        )

    #получаем тело запроса
    request_body = json.loads( request.body.decode( 'utf-8' ) )

    try:
        data = request_body["data"]
        user = User.objects.create_user(data["name"], data["mail"], data["password"])
        user.save()

        profile = Profile.objects.create(
            user=user
        )
    except:
        return JsonResponse (
            {
                'status': False,
                'comment': 'Произошла ошибка во время регистрации пользователя'
            }
        )

    organization = Company.objects.filter(organization_id=request_body["organization_id"]).first()

    if (organization):
        try:
            roles = request_body["roles"]
            organization_roles = Role.objects.filter(Q(company=organization) & Q(title__in=roles))

            access_levels = request_body["access_level"]

            for role in organization_roles:
                profile.roles.add(role)

            for key in access_levels:
                section = Section.objects.filter(Q(title=key) & Q(company=organization)).first()
                access_level_user = AccessLevel_Section_User.objects.create (
                    user=profile,
                    section=section,
                    access_level=access_levels[key]
                )
                access_level_user.save()

            profile.save()

        except:
            return JsonResponse (
                {
                    'status': False,
                    'comment': 'Произошла ошибка во время присвоения роли'
                }
            )
    else:
        return JsonResponse (
            {
                'status': False,
                'comment': 'Неправильный код организации'
            }
        )



    return JsonResponse( { "status": True } )
