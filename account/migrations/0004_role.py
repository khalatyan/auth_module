# Generated by Django 2.2.20 on 2021-05-27 03:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_section'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512, verbose_name='Уровень доступа')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Company', verbose_name='Компания')),
            ],
            options={
                'verbose_name': 'Роль пользователя',
                'verbose_name_plural': 'Роли пользователя',
            },
        ),
    ]