# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-11-02 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eoip', '0004_auto_20181102_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eoiptunnelconfig',
            name='interface',
            field=models.CharField(default=b'tap0', max_length=40, verbose_name='EOIP interface'),
        ),
    ]
