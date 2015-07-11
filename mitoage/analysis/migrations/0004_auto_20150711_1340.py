# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_statscache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statscache',
            name='stats_dump',
            field=models.TextField(verbose_name=b'Cached stats'),
        ),
        migrations.AlterUniqueTogether(
            name='statscache',
            unique_together=set([('group_type', 'taxon_id', 'group_section')]),
        ),
    ]
