# Generated by Django 2.0.1 on 2018-06-12 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0002_auto_20180612_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='action',
            field=models.CharField(default='', max_length=32),
        ),
    ]
