from import_export import resources
from import_export.fields import Field

from django.contrib.auth.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        exclude = (
            "id", "password", "last_login",
            "groups", "user_permissions", "username",
            "first_name", "last_name", "is_staff",
            "is_active", "date_joined", "is_superuser"
        )

    email = Field(attribute='email', column_name='E-mail')
    profile__name = Field(attribute='profile__name', column_name='Имя и фамилия')
    profile__phone = Field(attribute='profile__phone', column_name='Телефон')
