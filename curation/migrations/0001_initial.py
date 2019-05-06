# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('contenttypes.contenttype',),
        ),
    ]
