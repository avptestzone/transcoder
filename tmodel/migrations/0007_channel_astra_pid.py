# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-21 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmodel', '0006_auto_20160902_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='astra_pid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]