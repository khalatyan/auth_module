import requests
import json
import datetime
import hashlib
import uuid
import jwt

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import authenticate


from django.contrib.auth.models import User
from account.models import *


class PersonalAccountView(TemplateView):
    template_name = 'index.html'


    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()

        return redirect('/roles')


class RolesView(TemplateView):
    template_name = 'roles.html'


    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()

        company = Company.objects.filter(moderator=self.request.user).first()
        roles = Role.objects.filter(company=company)
        access_levels = AccessLevel_Section_Role.objects.filter(role__in=roles)

        roles_items = []

        for role in roles:
            access_levels = AccessLevel_Section_Role.objects.filter(role=role)
            roles_items.append([role, access_levels])

        context = super().get_context_data(**kwargs)
        context["role"] = True
        context["roles"] = roles_items
        response = render(request, self.template_name, context)

        return response


class ProfilesView(TemplateView):
    template_name = 'profiles.html'


    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()

        company = Company.objects.filter(moderator=self.request.user).first()
        roles = Role.objects.filter(company=company)

        profiles_item = []
        profiles = Profile.objects.filter(roles__in=roles).distinct()
        for profile in profiles:
            profiles_item.append([profile, profile.roles.values_list('title', flat=True)])

        context = super().get_context_data(**kwargs)
        context["profile"] = True
        context["profiles"] = profiles_item
        response = render(request, self.template_name, context)

        return response



def single_profile(request, profile_id):
    if not request.user.is_superuser:
        raise PermissionDenied()

    company = Company.objects.filter(moderator=request.user).first()
    profile = Profile.objects.filter(id=profile_id).first()
    all_roles = Role.objects.filter(company=company)
    profile_roles = profile.roles.values_list('title', flat=True)

    access_level_roles = AccessLevel_Section_User.objects.filter(user=profile)
    sections = Section.objects.filter(company=company)

    response = render(request, 'single_profile.html', locals())
    response['Cache-Control'] = 'no-cache, must-revalidate'
    return response




@csrf_exempt
@transaction.atomic
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
        user = User.objects.filter(username=data["name"])
        if not user:
            user = User.objects.create_user(data["name"], data["mail"], data["password"])
            user.save()

            profile = Profile.objects.create(
                user=user
            )
            profile.save()
        else:
            return JsonResponse (
                {
                    'status': False,
                    'comment': 'Имя пользователя уже зарегистрирована'
                }
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

                if (section and profile):
                    access_level_user = AccessLevel_Section_User.objects.create (
                        user=profile,
                        section=section,
                        access_level=access_levels[key]
                    )
                access_level_user.save()

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



    return JsonResponse(
        {
            "status": True,
            "token": str(_generate_jwt_token(profile, request_body["organization_id"]))
        }
    )


@csrf_exempt
@transaction.atomic
def auth( request ):

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
        organization_id = request_body["organization_id"]
        user = authenticate(username=data["name"], password=data["password"])

        if user is not None:
            profile = Profile.objects.filter(user=user).first()
            token = _generate_jwt_token(profile, organization_id)

            return JsonResponse (
                {
                    'status': True,
                    'token': str(token)
                }
            )

        else:
            return JsonResponse (
                {
                    'status': False,
                    'comment': 'Такого пользователя не существует'
                }
            )
    except:
        return JsonResponse (
            {
                'status': False,
                'comment': 'Произошла неизвестная ошибка во аутентификации пользователя'
            }
        )


@csrf_exempt
@transaction.atomic
def auth_for_organization( request ):

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
        organization_id = request_body["organization_id"]
        user = authenticate(username=data["name"], password=data["password"])

        if user is not None:
            profile = Profile.objects.filter(user=user).first()

            try:
                organization = Company.objects.filter(organization_id=request_body["organization_id"]).first()
                roles = request_body["roles"]
                organization_roles = Role.objects.filter(Q(company=organization) & Q(title__in=roles))
                access_levels = request_body["access_level"]

                for role in organization_roles:
                    profile.roles.add(role)

                for key in access_levels:
                    section = Section.objects.filter(Q(title=key) & Q(company=organization)).first()

                    if (section and profile):
                        access_level_user = AccessLevel_Section_User.objects.create (
                            user=profile,
                            section=section,
                            access_level=access_levels[key]
                        )
                    access_level_user.save()
            except:
                return JsonResponse (
                    {
                        'status': False,
                        'comment': 'Произошла ошибка во время присвоения роли'
                    }
                )

            token = _generate_jwt_token(profile, organization_id)

            return JsonResponse (
                {
                    'status': True,
                    'token': str(token)
                }
            )

        else:
            return JsonResponse (
                {
                    'status': False,
                    'comment': 'Такого пользователя не существует'
                }
            )
    except:
        return JsonResponse (
            {
                'status': False,
                'comment': 'Произошла неизвестная ошибка во аутентификации пользователя'
            }
        )


def get_profile_access_levels(profile, self_organization_id):
    dt = datetime.now() + timedelta(days=1)
    access_levels = AccessLevel_Section_User.objects.filter(user=profile)
    access_level_token = {
        "access_levels": [],
        "roles": [],
        'id': profile.id,
        'exp': dt.utcfromtimestamp(dt.timestamp()),
    }
    for access_level in access_levels:
        if (access_level.section.company.organization_id == self_organization_id):
            access_level_token["access_levels"].append({
                "section": access_level.section.title,
                "access_level": access_level.access_level
            })

    roles = profile.roles.values_list('id', flat=True)
    for role in roles:
        role_item = Role.objects.filter(id=role).first()
        if role_item.company.organization_id == self_organization_id:
            access_level_token["roles"].append(role_item.title)

    print (access_level_token)
    return access_level_token


def _generate_jwt_token(profile, organization_id):
    token = jwt.encode(get_profile_access_levels(profile, organization_id), settings.SECRET_KEY, algorithm='HS256')

    print(token)
    return token
