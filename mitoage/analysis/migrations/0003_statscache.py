# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_auto_20150630_2151'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatsCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_type', models.IntegerField(default=1, max_length=1, verbose_name=b'Type of group', choices=[(1, b'All species'), (2, b'Class'), (3, b'Order'), (4, b'Family')])),
                ('taxon_id', models.IntegerField(max_length=11, verbose_name=b'Taxon ID')),
                ('group_section', models.CharField(max_length=20, verbose_name=b'Section of mtDNA')),
                ('group_size', models.IntegerField(max_length=5, verbose_name=b'Size of group')),
                ('stats_dump', models.TextField(verbose_name=b'Stats')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
