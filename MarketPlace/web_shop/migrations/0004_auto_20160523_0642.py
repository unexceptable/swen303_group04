# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-23 06:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web_shop', '0003_address_visible'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatnotification',
            old_name='origin',
            new_name='notif',
        ),
        migrations.AddField(
            model_name='chatnotification',
            name='link',
            field=models.CharField(default=datetime.datetime(2016, 5, 23, 6, 42, 53, 476068, tzinfo=utc), max_length=100),
            preserve_default=False,
        ),
    ]