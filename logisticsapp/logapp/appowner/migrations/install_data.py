# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 14:22
'''
 * Rwanda Law Reform Comission
 *
 * Developed by Sium, Kigali, Rwanda 2016-2017. All Rights Reserved
 *
 * This content is protected by national and international patent laws.
 *
 * Possession and access to this content is granted exclusively to Developers
 * of RLRC and Sium, while full ownership is granted only to Rwanda Law Reform Comission.
 
 *
 * @package	RLWC - LRC
 * @author	Kiflemariam Sium (kmsium@gmail.com || sium@go.rw || sium@iconicdatasystems.com)
 * @copyright	Copyright (c) RLCR Limited, 2017
 * @license	http://
 * @link	http://
 * @since	Version 1.0.0
 * @filesource
 '''
from __future__ import unicode_literals

from django.db import migrations

def insert_go_information():
    from app.conf import base as settings
    import os
    sql_statements = open(os.path.join(settings.BASE_DIR,'appowner/sql/information.sql'), 'r').read()
    return sql_statements


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ('appowner', '0001_initial'),
    ]

    operations = [
        
        migrations.RunSQL(insert_go_information()),
    ]
