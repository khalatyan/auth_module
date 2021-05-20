from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'Организации'

    title  = models.CharField(verbose_name='Организация', max_length=512)
    moderator_for = models.ForeignKey(User, verbose_name='Модератор для организации', blank=True, null=True, on_delete=models.SET_NULL)

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
    company = models.ForeignKey(Company, verbose_name='Организация', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username or '-'


class Section(models.Model):
    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'Разделы'

    title  = models.CharField(verbose_name='Раздел', max_length=512)
    company = models.ForeignKey(Company, verbose_name='Организация', blank=True, null=True, on_delete=models.SET_NULL)


class AccessLevel(models.Model):
    class Meta:
        verbose_name = 'уровень доступа'
        verbose_name_plural = 'Уровни доступа'

    title  = models.CharField(verbose_name='Уровень доступа', max_length=512)

    def __str__(self):
        return self.title or '-'


class UserAccessLevel(models.Model):
    class Meta:
        verbose_name = 'уровень доступа для раздела'
        verbose_name_plural = 'Уровни доступа для раздела'

    user = models.ForeignKey(verbose_name='Пользователь', to=Profile, unique=False, on_delete=models.CASCADE)
    section = models.ForeignKey(verbose_name='Раздел', to=Section, unique=False, on_delete=models.CASCADE)
    access_level = models.ForeignKey(verbose_name='Уровень доступа', to=AccessLevel, unique=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.access_level.title or '-'
