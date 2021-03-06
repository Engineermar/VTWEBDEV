# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-24 23:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BnbHost',
            fields=[
                ('host_id', models.IntegerField(primary_key=True, serialize=False)),
                ('host_name', models.CharField(max_length=200)),
                ('host_since', models.DateField(blank=True, null=True)),
                ('host_url', models.URLField(blank=True, max_length=2000, null=True)),
                ('host_location', models.CharField(blank=True, max_length=2000, null=True)),
                ('about_host', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Airbnb Host',
                'verbose_name_plural': 'Airbnb Hosts',
                'db_table': 'airbnb_host',
            },
        ),
        migrations.CreateModel(
            name='BnbListing',
            fields=[
                ('listing_id', models.IntegerField(primary_key=True, serialize=False)),
                ('listing_url', models.URLField(blank=True, max_length=2000, null=True)),
                ('listing_name', models.CharField(blank=True, max_length=2000, null=True)),
                ('listing_summary', models.TextField(blank=True, null=True)),
                ('listing_space', models.TextField(blank=True, null=True)),
                ('listing_description', models.TextField(blank=True, null=True)),
                ('listing_house_rule', models.TextField(blank=True, null=True)),
                ('picture_url', models.URLField(blank=True, max_length=2000, null=True)),
                ('neighbourhood', models.CharField(blank=True, max_length=2000, null=True)),
                ('city', models.CharField(blank=True, max_length=2000, null=True)),
                ('state', models.CharField(blank=True, max_length=2000, null=True)),
                ('zip', models.IntegerField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.CharField(blank=True, max_length=100, null=True)),
                ('longitude', models.CharField(blank=True, max_length=100, null=True)),
                ('max_accomodation', models.IntegerField(blank=True, null=True)),
                ('json_amenities', models.TextField(blank=True, null=True)),
                ('number_of_reviews', models.IntegerField(blank=True, null=True)),
                ('review_per_month', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('review_scores_rating', models.IntegerField(blank=True, null=True)),
                ('host_id', models.ForeignKey(db_column='host_id', on_delete=django.db.models.deletion.CASCADE, to='airbnb.BnbHost')),
            ],
            options={
                'verbose_name': 'Airbnb Listing',
                'verbose_name_plural': 'Airbnb Listings',
                'db_table': 'airbnb_listing',
            },
        ),
        migrations.CreateModel(
            name='BnbReview',
            fields=[
                ('review_id', models.IntegerField(primary_key=True, serialize=False)),
                ('review_date', models.DateField(blank=True, null=True)),
                ('reviewer_name', models.CharField(blank=True, max_length=100, null=True)),
                ('host_id', models.ForeignKey(db_column='host_id', on_delete=django.db.models.deletion.CASCADE, to='airbnb.BnbHost')),
                ('listing_id', models.ForeignKey(db_column='listing_id', on_delete=django.db.models.deletion.CASCADE, to='airbnb.BnbListing')),
            ],
            options={
                'verbose_name': 'Airbnb Listing Review',
                'verbose_name_plural': 'AAirbnb Listing Reviews',
                'db_table': 'airbnb_listing_reviews',
            },
        ),
    ]
