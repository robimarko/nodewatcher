# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-13 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0005_auto_20160207_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='builder',
            name='metadata',
            field=models.TextField(blank=True, default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='buildresult',
            name='config',
            field=models.TextField(blank=True, default='{}', help_text='Configuration used to build this firmware.'),
        ),
    ]
