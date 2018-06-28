# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-06-28 03:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0003_permission_action'),
        ('crm', '0002_customerdistrbute'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='password',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='username',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.User'),
        ),
    ]
