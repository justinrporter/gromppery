# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-15 13:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('top', models.FileField(upload_to='')),
                ('mdp', models.FileField(upload_to='')),
                ('gro', models.FileField(upload_to='')),
            ],
        ),
    ]
