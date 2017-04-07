# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-07 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_transmitter_alive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transmitter',
            name='status',
        ),
        migrations.AddField(
            model_name='satellite',
            name='status',
            field=models.CharField(choices=[(b'a', b'Alive'), (b'd', b'Dead'), (b'r', b'Re-entered')], default=b'a', max_length=2),
        ),
    ]
