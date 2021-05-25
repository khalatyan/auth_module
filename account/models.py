from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'Организации'

    title  = models.CharField(verbose_name='Организация', max_length=512)

    def __str__(self):
        return self.title or '-'


class UserProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'


    def get_name(self):
        return str(self.profile)
    get_name.short_description = 'Имя и фамилия'
    get_name.allow_tags = True


class Profile(models.Model):
    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-user__date_joined']

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username or '-'


class Section(models.Model):
    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'Разделы'

    title  = models.CharField(verbose_name='Раздел', max_length=512)
    company = models.ForeignKey(verbose_name='Компания',to=Company,on_delete=models.CASCADE)


class AccessLevel(models.Model):
    class Meta:
        verbose_name = 'уровень доступа'
        verbose_name_plural = 'Уровни доступа'

    title  = models.CharField(verbose_name='Уровень доступа', max_length=512)
    description = models.TextField(verbose_name='Описание',null=True,blank=True)

    def __str__(self):
        return self.title or '-'


class Role(models.Model):
    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователя'

    title  = models.CharField(verbose_name='Уровень доступа', max_length=512)
    description = models.TextField(verbose_name='Описание',null=True,blank=True)
    company = models.ForeignKey(verbose_name='Компания',to=Company,on_delete=models.CASCADE)

    def __str__(self):
        return self.title or '-'
