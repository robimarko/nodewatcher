# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-13 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irnas_koruza', '0006_koruzalinkmonitor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='koruzalinkmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='koruzavpnmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]
