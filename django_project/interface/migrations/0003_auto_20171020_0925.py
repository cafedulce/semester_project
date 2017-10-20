# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 09:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0002_pyscenedetectargs'),
    ]

    operations = [
        migrations.AddField(
            model_name='pyscenedetectargs',
            name='duration',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pyscenedetectargs',
            name='end_time',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pyscenedetectargs',
            name='start_time',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pyscenedetectargs',
            name='stats_file',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='quiet_mode',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='save_images',
            field=models.BooleanField(default=False),
        ),
    ]
