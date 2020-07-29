# -*- coding: utf-8 -*-
from django.db import models, migrations  # noqa


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
