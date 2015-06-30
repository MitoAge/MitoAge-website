# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_a',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'A content', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_c',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'C content', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_g',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'G content', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_others',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'Other', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_size',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'Size of tRNA region of mtDNA', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitoageentry',
            name='bc_total_tRNA_t',
            field=models.IntegerField(max_length=11, null=True, verbose_name=b'T content', blank=True),
            preserve_default=True,
        ),
    ]
