# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-02 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='is_unknown',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='category',
            name='active',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='is_unknown',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='active',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='store',
            name='active',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='store',
            name='service',
            field=models.CharField(choices=[('Reserve', 'StoreIn'), ('Distribution', 'StoreInOut')], default='Distribution', max_length=30),
        ),
    ]
