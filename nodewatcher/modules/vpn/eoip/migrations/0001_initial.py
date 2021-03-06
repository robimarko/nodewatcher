# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-10-24 20:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cgm', '0022_json_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='EOIPTunnelConfig',
            fields=[
                ('packageconfig_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cgm.PackageConfig')),
                ('local_ip', models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name='Local IP adress')),
                ('remote_ip', models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name='Remote IP adress')),
                ('tunnel_id', models.PositiveIntegerField(default=0, verbose_name='Tunnel ID')),
                ('interface', nodewatcher.core.registry.fields.ReferenceChoiceField(blank=True, help_text='Select on which interface the broker should listen on.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cgm.InterfaceConfig')),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
            bases=('cgm.packageconfig',),
        ),
    ]
