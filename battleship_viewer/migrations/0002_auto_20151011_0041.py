# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battleship_viewer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='move',
            name='player1_text',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='move',
            name='player2_text',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
