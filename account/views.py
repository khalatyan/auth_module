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

ACCESS_LEVEL = {
    1: 'Запрет',
    2: 'Чтение',
    3: 'Редактирование',
}

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

        warning = False

        if "delete" in request.GET:
            delete_id = request.GET.get("delete")
            try:
                object = AccessLevel_Section_Role.objects.get(id=delete_id)
                this_role = object.role
                access_level_section = object.section
                access_level_acces_level = object.access_level

                peoples = Profile.objects.filter(roles__in=[this_role])
                object.delete()

                for profile in peoples:
                    access_level_user = AccessLevel_Section_User.objects.filter(Q(user=profile) & \
                        Q(section=access_level_section) & Q(access_level=access_level_acces_level))
                    if access_level_user:
                        access_level_user.delete()
            except:
                warning = "Ошибка удаления уровня доступа"

        elif "add" in request.GET:
            section_new = Section.objects.get(id=request.GET.get("section"))
            role_new = Role.objects.get(id=request.GET.get("role"))
            access_level_new = request.GET.get("access_level")

            object = AccessLevel_Section_Role.objects.filter(Q(role=role_new) & Q(section=section_new))

            if (object):
                warning = "Уже указан уровень доступа для этого раздела"
            else:
                peoples = Profile.objects.filter(roles__in=[role_new])
                for profile in peoples:
                    access_level_user = AccessLevel_Section_User.objects.filter(Q(user=profile) & \
                        Q(section=section_new)).first()
                    if access_level_user:
                        if int(access_level_user.access_level) <= int(access_level_new):
                            access_level_user.access_level = access_level_new
                    else:
                        access_level_user = AccessLevel_Section_User.objects.create(
                            user=profile,
                            section=section_new,
                            access_level=access_level_new
                        )
                    access_level_user.save()

                object = AccessLevel_Section_Role.objects.create(
                    role=role_new,
                    section=section_new,
                    access_level=access_level_new
                )
                object.save()
        elif "add_role" in request.GET:
            role_title = request.GET.get("role")
            company = Company.objects.filter(moderator=self.request.user).first()
            role = Role.objects.filter(title=role_title)

            if (role):
                warning="Такая роль уже существует"
            else:
                role = Role.objects.create(
                    title=role_title,
                    company=company
                )
                role.save()
        elif "del_role" in request.GET:
            role_id = request.GET.get("role_id")
            try:
                role = Role.objects.get(id=role_id)
                acces_level_roles = AccessLevel_Section_Role.objects.filter(role=role)

                peoples = Profile.objects.filter(roles__in=[role])
                for profile in peoples:
                    for access_level_role in acces_level_roles:
                        access_level_user = AccessLevel_Section_User.objects.filter(Q(user=profile) & \
                            Q(section=access_level_role.section) & Q(access_level=access_level_role.access_level)).first()
                        if access_level_user:
                            access_level_user.delete()

                role.delete()
            except:
                warning = "Ошибка удаления роли"
        else:
            for elem_id in request.GET:
                access_level_value = request.GET.get(elem_id)

                try:
                    object = AccessLevel_Section_Role.objects.get(id=elem_id)

                    peoples = Profile.objects.filter(roles__in=[object.role])
                    for profile in peoples:
                        access_level_user = AccessLevel_Section_User.objects.filter(Q(user=profile) & \
                            Q(section=object.section)).first()
                        if access_level_user:
                            if int(access_level_user.access_level) <= int(access_level_value):
                                access_level_user.access_level = access_level_value
                        else:
                            access_level_user = AccessLevel_Section_User.objects.create(
                                user=profile,
                                section=object.section,
                                access_level=access_level_value
                            )
                        access_level_user.save()

                    object.access_level = access_level_value
                    object.save()
                except:
                    warning = "Ошибка при редактировании уровня доступа"

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
        context["all_access_levels"] = [
            [1, 'Запрет'],
            [2, 'Чтение'],
            [3, 'Редактирование'],
        ]
        context["all_sections"] = Section.objects.filter(company=company)
        context["all_roles"] = Role.objects.filter(company=company)
        context["warning"] = warning
        response = render(request, self.template_name, context)

        return response


class ProfilesView(TemplateView):
    template_name = 'profiles.html'


    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()

        warning = False

        company = Company.objects.filter(moderator=self.request.user).first()
        roles = Role.objects.filter(company=company)

        if "delete_role" in self.request.GET:
            user_id = self.request.GET.get("delete_role")
            profile = Profile.objects.get(id=user_id)
            profile_roles_ = profile.roles.values_list('id', flat=True)
            profile_roles = Role.objects.filter(Q(id__in=profile_roles_) & Q(company=company)).distinct()

            for role in profile_roles:
                profile.roles.remove(role)


        profiles_item = []
        profiles = Profile.objects.filter(roles__in=roles).distinct()

        for profile in profiles:
            profile_roles_ = profile.roles.values_list('id', flat=True)
            profile_roles = Role.objects.filter(Q(id__in=profile_roles_) & Q(company=company)).distinct()
            profiles_item.append([profile, profile_roles])

        context = super().get_context_data(**kwargs)
        context["profile"] = True
        context["profiles"] = profiles_item
        response = render(request, self.template_name, context)

        return response



def single_profile(request, profile_id):
    if not request.user.is_superuser:
        raise PermissionDenied()

    warning = False
    if "del_role" in request.GET:
        profile = Profile.objects.filter(id=profile_id).first()
        role_id = request.GET.get("role_id")
        try:
            my_role = Role.objects.get(id=role_id)
            access_levels_role = AccessLevel_Section_Role.objects.filter(role=my_role)

            for access_level_role in access_levels_role:
                access_level_user = AccessLevel_Section_User.objects.filter( \
                    Q(section=access_level_role.section) \
                    & Q(access_level=access_level_role.access_level)).first()
                if access_level_user:
                    access_level_user.delete()
            profile.roles.remove(my_role)
        except:
            warning = "Ошибка во время удаления роли"

    elif "add_new_role" in request.GET:
        profile = Profile.objects.filter(id=profile_id).first()
        role_id = request.GET.get("role_id")
        try:
            my_role = Role.objects.get(id=role_id)
            profile.roles.add(my_role)

            access_levels_role = AccessLevel_Section_Role.objects.filter(role=my_role)

            for access_level_role in access_levels_role:
                access_level_user = AccessLevel_Section_User.objects.filter(\
                    Q(user=profile) & Q(section=access_level_role.section))
                if access_level_user:
                    if int(access_level_user.access_level) <= int(access_level_role.access_level):
                        access_level_user.access_level = access_level_role.access_level
                else:
                    access_level_user = AccessLevel_Section_User.objects.create(
                        user=profile,
                        section=access_level_role.section,
                        access_level=access_level_role.access_level
                    )
        except:
            warning = "Ошибка во время добавления роли"

    elif "add_new_access_level" in request.GET:
        section_id = request.GET.get("section_id")
        access_level_id = request.GET.get("access_level_id")
        access_level_user = AccessLevel_Section_User.objects.filter(section=section_id)
        profile = Profile.objects.filter(id=profile_id).first()

        if (access_level_user):
            warning="Уровень досутпа для этого раздела уже задан"
        else:
            section = Section.objects.get(id=section_id)
            access_level_user = AccessLevel_Section_User.objects.create(
                section=section,
                access_level=access_level_id,
                user=profile
            )
            access_level_user.save()
    elif "del_access_level" in request.GET:
        access_level_id = request.GET.get("access_level")
        try:
            access_level_item = AccessLevel_Section_User.objects.get(id=access_level_id)
            access_level_item.delete()
        except:
            print("Не удается удалить")
    elif "edit_access_level" in request.GET:
        access_level_item = AccessLevel_Section_User.objects.get(id=request.GET.get("access_level_id"))
        access_level_value = request.GET.get("access_level_value")

        access_level_item.access_level = access_level_value
        access_level_item.save()


    company = Company.objects.filter(moderator=request.user).first()
    profile = Profile.objects.filter(id=profile_id).first()
    profile_roles_ = profile.roles.values_list('id', flat=True)
    profile_roles = Role.objects.filter(Q(id__in=profile_roles_) & Q(company=company)).distinct()
    all_roles = Role.objects.filter(company=company).exclude(id__in=profile_roles_)

    company_section = Section.objects.filter(company=company)

    access_level_roles = AccessLevel_Section_User.objects.filter(Q(user=profile) & Q(section__in=company_section))
    sections = Section.objects.filter(company=company)
    all_access_levels = [
                [1, 'Запрет'],
                [2, 'Чтение'],
                [3, 'Редактирование'],
    ]

    response = render(request, 'single_profile.html', locals())
    response['Cache-Control'] = 'no-cache, must-revalidate'
    return response

class SectionsView(TemplateView):
    template_name = 'section.html'


    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()

        company = Company.objects.filter(moderator=self.request.user).first()
        all_sections = Section.objects.filter(company=company)
        parent_secions = Section.objects.filter(Q(company=company) & Q(parent=None))

        if "del_section" in request.GET:
            section = Section.objects.filter(id=request.GET.get("section")).first()
            if section.get_children_bool():
                del_children(section)
            section.delete()

        if "add_section" in request.GET:
            parent = Section.objects.filter(id=request.GET.get("parent")).first()
            value = request.GET.get("value")
            if parent:
                section = Section.objects.create(
                    title=value,
                    parent=parent,
                    company=company
                )
            else:
                section = Section.objects.create(
                    title=value,
                    company=company
                )
            section.save()

            if parent:
                access_levels = AccessLevel_Section_Role.objects.filter(section=parent)

                for access_level in access_levels:
                    new_access_level = AccessLevel_Section_Role.objects.create(
                        role=access_level.role,
                        section=section,
                        access_level=access_level.access_level
                    )
                    new_access_level.save()



        context = super().get_context_data(**kwargs)
        context["section_link"] = True
        context["all_sections"] = all_sections
        context["parent_secions"] = parent_secions
        response = render(request, self.template_name, context)

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
                acces_level_roles = AccessLevel_Section_Role.objects.filter(role=role)
                for acces_level_role in acces_level_roles:
                    _set_access_level_user_from_role(
                        profile=profile,
                        section=acces_level_role.section,
                        access_level=acces_level_role.access_level
                    )

            for key in access_levels:
                section = Section.objects.filter(Q(title=key) & Q(company=organization)).first()

                if (section and profile):
                    _set_access_level_user_from_role(
                        profile=profile,
                        section=section,
                        access_level=access_levels[key]
                    )

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
                    acces_level_roles = AccessLevel_Section_Role.objects.filter(role=role)
                    for acces_level_role in acces_level_roles:
                        _set_access_level_user_from_role(
                            profile=profile,
                            section=acces_level_role.section,
                            access_level=acces_level_role.access_level
                        )

                for key in access_levels:
                    section = Section.objects.filter(Q(title=key) & Q(company=organization)).first()

                    if (section and profile):
                        _set_access_level_user_from_role(
                            profile=profile,
                            section=section,
                            access_level=access_levels[key]
                        )
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

    return access_level_token


def _generate_jwt_token(profile, organization_id):
    token = jwt.encode(get_profile_access_levels(profile, organization_id), settings.SECRET_KEY, algorithm='HS256')

    return token

def _set_access_level_user_from_role(profile, access_level, section):
    access_level_user = AccessLevel_Section_User.objects.filter(Q(user=profile) & Q(section=section)).first()

    if access_level_user:
        if int(access_level) > access_level_user.access_level:
            access_level_user.access_level = access_level
            access_level_user.save()
    else:
        access_level_user = AccessLevel_Section_User.objects.create(
            user=profile,
            section=section,
            access_level=access_level
        )
        access_level_user.save()

def getChildren(section):
    children = Section.objects.filter(parent=section)
    return children
    # OR just format the data so it's returned in the format you like
    # or you can return them as Person objects and have another method
    # to transform each object in the format you like (e.g Person.asJSON())


def del_children(obj):
    children = obj.get_children()
    for child in children:
        if child.get_children_bool():
            del_children(child)
        child.delete()
