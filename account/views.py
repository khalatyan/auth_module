import requests
import json
import datetime
import hashlib
import uuid

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import transaction


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
                section = Section.objects.filter(Q(title=key) & Q(company=organization))
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


@csrf_exempt
@transaction.atomic
def auth( request ):
    profiles = Profile.objects.all()
    l = []
    for p in profiles:
        l.append(p.token)

    return JsonResponse( { "status": l } )
