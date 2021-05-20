# Generated by Django 2.0 on 2021-05-20 14:02

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512, verbose_name='Уровень доступа')),
            ],
            options={
                'verbose_name': 'уровень доступа',
                'verbose_name_plural': 'Уровни доступа',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512, verbose_name='Организация')),
            ],
            options={
                'verbose_name': 'организация',
                'verbose_name_plural': 'Организации',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Company', verbose_name='Организация')),
                ('moderator_for', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderator_for', to='account.Company', verbose_name='Модератор для организации')),
            ],
            options={
                'verbose_name': 'профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
                'ordering': ['-user__date_joined'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512, verbose_name='Раздел')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Company', verbose_name='Организация')),
            ],
            options={
                'verbose_name': 'раздел',
                'verbose_name_plural': 'Разделы',
            },
        ),
        migrations.CreateModel(
            name='UserAccessLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.AccessLevel')),
                ('section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.Section')),
            ],
            options={
                'verbose_name': 'уровень доступа для раздела',
                'verbose_name_plural': 'Уровни доступа для раздела',
            },
        ),
        migrations.CreateModel(
            name='UserProxy',
            fields=[
            ],
            options={
                'verbose_name': 'пользователь',
                'verbose_name_plural': 'Пользователи',
                'proxy': True,
                'indexes': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='useraccesslevel',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
