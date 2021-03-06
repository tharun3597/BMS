# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-12 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Register',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('factid', models.IntegerField(null=True)),
                ('course', models.CharField(choices=[('SE', 'Software Engineering'), ('BIS', 'Business Information Systems'), ('DBMS', 'Database Management Systems'), ('TC', 'Technical Communication'), ('CN', 'Computer Networks'), ('LP', 'Language Processors')], max_length=4, unique=True)),
                ('password', models.CharField(max_length=20)),
                ('approval', models.BooleanField(default=False)),
            ],
        ),
    ]
