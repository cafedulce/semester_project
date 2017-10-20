# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0003_auto_20171020_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='block_size',
            field=models.IntegerField(default=8),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='detection_method',
            field=models.CharField(default=b'content', max_length=255),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='downscale_factor',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='fade_bias',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='frame_skip',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='min_percent',
            field=models.IntegerField(default=95),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='min_scene_len',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='pyscenedetectargs',
            name='threshold',
            field=models.IntegerField(default=30),
        ),
    ]
