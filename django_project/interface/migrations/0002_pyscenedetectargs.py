# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 07:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PySceneDetectArgs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('detection_method', models.CharField(max_length=255)),
                ('threshold', models.IntegerField()),
                ('min_percent', models.IntegerField()),
                ('min_scene_len', models.IntegerField()),
                ('block_size', models.IntegerField()),
                ('fade_bias', models.IntegerField()),
                ('downscale_factor', models.IntegerField()),
                ('frame_skip', models.IntegerField()),
                ('save_images', models.BooleanField()),
                ('quiet_mode', models.BooleanField()),
            ],
        ),
    ]
