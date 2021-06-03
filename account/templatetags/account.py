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
from django import template
from django.db import transaction
from django.contrib.auth import authenticate


from django.contrib.auth.models import User
from account.models import *

import datetime

register = template.Library()

@register.simple_tag
def getChildren(section):
    children = Section.objects.filter(parent=section)
    return children
    # OR just format the data so it's returned in the format you like
    # or you can return them as Person objects and have another method
    # to transform each object in the format you like (e.g Person.asJSON())
