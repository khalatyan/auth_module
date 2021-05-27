import uuid

from django.db import models
from django.contrib.auth.models import User

from mptt.models import MPTTModel, TreeForeignKey

ACCESS_LEVEL = [
    (1, 'Read (R)'),
    (2, 'Insert (I)'),
    (3, 'Update (U)'),
    (4, 'Delete (D)'),
    (5, 'Execute (E)')
]

class Company(models.Model):
    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'Организации'

    title  = models.CharField(verbose_name='Организация', max_length=512)
    moderator = models.ManyToManyField(User, verbose_name="Модератор")
    organization_id = models.CharField(verbose_name="ID организации", max_length=126, default=uuid.uuid4())

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


class Section(MPTTModel):
    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'Разделы'

    parent = TreeForeignKey('self', verbose_name=u'Родитель', blank=True, null=True, on_delete=models.SET_NULL)
    title  = models.CharField(verbose_name='Раздел', max_length=512)
    company = models.ForeignKey(verbose_name='Компания',to=Company,on_delete=models.CASCADE)

    def __str__(self):
        return self.title or '-'

    class MPTTMeta:
        order_insertion_by = ['title']


class Role(models.Model):
    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователя'

    title  = models.CharField(verbose_name='Уровень доступа', max_length=512)
    description = models.TextField(verbose_name='Описание',null=True,blank=True)
    company = models.ForeignKey(verbose_name='Компания',to=Company,on_delete=models.CASCADE)

    def __str__(self):
        return self.title or '-'

class Profile(models.Model):
    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-user__date_joined']

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='profile')
    roles = models.ManyToManyField(Role, verbose_name="Роли пользователя")

    def __str__(self):
        return self.user.username or '-'


class AccessLevel_Section_User(models.Model):
    class Meta:
        verbose_name = 'уровень доступа для раздела(для пользователя)'
        verbose_name_plural = 'уровни доступа для раздела(для пользователя)'
        ordering = ['section']

    user = models.ForeignKey(to=Profile, on_delete=models.CASCADE, verbose_name="Пользователь")
    section = models.ForeignKey(to=Section, on_delete=models.CASCADE, verbose_name="Раздел")
    access_level = models.IntegerField(verbose_name='Уровень досутпа', choices=ACCESS_LEVEL, default=1)

    def __str__(self):
        return self.user.user.username or '-'


class AccessLevel_Section_Role(models.Model):
    class Meta:
        verbose_name = 'уровень доступа для раздела(для роли)'
        verbose_name_plural = 'уровни доступа для раздела(для роли)'
        ordering = ['section']

    role = models.ForeignKey(to=Role, on_delete=models.CASCADE, verbose_name="Роль", null=True)
    section = models.ForeignKey(to=Section, on_delete=models.CASCADE, verbose_name="Раздел")
    access_level = models.IntegerField(verbose_name='Уровень досутпа', choices=ACCESS_LEVEL, default=1)

    def __str__(self):
        return self.role.title or '-'
