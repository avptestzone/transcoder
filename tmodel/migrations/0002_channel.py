# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-20 11:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmodel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('multicast_in', models.CharField(max_length=25)),
                ('multicast_out', models.CharField(max_length=25)),
                ('command', models.TextField()),
                ('status', models.BooleanField()),
            ],
        ),
    ]
