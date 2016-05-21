# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-21 06:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_shop', '0002_auto_20160520_0019'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=50)),
                ('message_type', models.CharField(choices=[(b'refunds', b'Refund and Cancellation'), (b'missing', b'Where is my stuff?'), (b'violation', b'Report violation of Terms of Service'), (b'phishing', b'Report a phishing incident'), (b'general', b'Report general issue')], default=b'general', max_length=20)),
                ('message', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[(b'open', b'Open'), (b'close', b'Closed')], default=b'open', max_length=6)),
            ],
        ),
    ]