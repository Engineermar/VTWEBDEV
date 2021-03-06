# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-31 09:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_id', models.CharField(max_length=30)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('processedon', models.DateField()),
                ('provider_reference', models.CharField(blank=True, max_length=35, null=True)),
                ('internal_reference', models.CharField(blank=True, max_length=35, null=True)),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_incominginvoice', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IncomingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('expire_on', models.DateField(blank=True, null=True)),
                ('tag', models.CharField(blank=True, max_length=35, null=True)),
                ('arrival_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('arrivedon', models.DateField()),
                ('current_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('collection_id', models.CharField(blank=True, max_length=255, null=True)),
                ('manf_serial', models.CharField(blank=True, max_length=30, null=True)),
                ('institution_code', models.CharField(blank=True, max_length=30, null=True)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_item_brand', to='inventory.Brand')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_item_invoice', to='logistic.IncomingInvoice')),
                ('manf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_item_manf', to='inventory.Manufacturer')),
                ('placed_in_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomingitem_store', to='inventory.Store')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_incomingitem', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_item_product', to='inventory.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ItemInStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=35)),
                ('arrivedon', models.DateField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='iteminstore_incomingitem', to='logistic.IncomingItem')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_iteminstore', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='iteminstore_store', to='inventory.Store')),
            ],
        ),
        migrations.CreateModel(
            name='ItemUnconventionalHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportedon', models.DateField()),
                ('factor', models.CharField(max_length=65)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unconventionalhistory_item', to='logistic.IncomingItem')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_unconventionalhistory', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OutgoingInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipent_type', models.CharField(choices=[('Office', 'Office'), ('Employee', 'Employee'), ('Unit', 'Unit'), ('Head', 'Head'), ('Department', 'Department'), ('Division', 'Division')], max_length=30)),
                ('system_id', models.CharField(max_length=30)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('processedon', models.DateField()),
                ('note', models.CharField(blank=True, max_length=3000, null=True)),
                ('internal_reference', models.CharField(blank=True, max_length=35, null=True)),
                ('direction', models.CharField(choices=[('Direct', 'Direct'), ('Transfer', 'Transfer')], default='Direct', max_length=30)),
                ('transfered_from_type', models.CharField(choices=[('Office', 'Office'), ('Employee', 'Employee'), ('Unit', 'Unit'), ('Head', 'Head'), ('Department', 'Department'), ('Division', 'Division')], max_length=30)),
                ('is_void', models.PositiveIntegerField(default=0)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dept_outgoinginvoice', to='hr.Department')),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='div_outgoinginvoice', to='hr.Division')),
                ('give_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_outgoinginvoice_givento', to='hr.Employee')),
                ('head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='head_outgoinginvoice', to='hr.Head')),
                ('office', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='office_outgoinginvoice', to='hr.Office')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_outgoinginvoice', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OutgoingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('given_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('given_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('ownership_status', models.PositiveIntegerField(choices=[(1, 'InPossession'), (2, 'Returned'), (3, 'Lost'), (4, 'Consumed'), (5, 'Transfered')], default=1)),
                ('collection_id', models.CharField(blank=True, max_length=255, null=True)),
                ('transfered_item_id', models.PositiveIntegerField(default=0)),
                ('arrived_to_store', models.DateField(blank=True, default=None, null=True)),
                ('given_from_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoingitem_store', to='inventory.Store')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoingitem_outgoinginvoice', to='logistic.OutgoingInvoice')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoingitem_incomingitem', to='logistic.IncomingItem')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_outgoingitem', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('identification', models.CharField(blank=True, max_length=30, null=True)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('phone', models.CharField(blank=True, max_length=13, null=True)),
                ('email', models.CharField(blank=True, max_length=35, null=True)),
                ('www', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=3000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProviderKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_providerkind', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
        ),
        migrations.CreateModel(
            name='RequestInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipent_type', models.CharField(choices=[('Office', 'Office'), ('Employee', 'Employee'), ('Unit', 'Unit'), ('Head', 'Head'), ('Department', 'Department'), ('Division', 'Division')], max_length=30)),
                ('processedon', models.DateField()),
                ('system_id', models.CharField(max_length=30)),
                ('confirmed', models.PositiveIntegerField(default=0)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dept_requestinvoice', to='hr.Department')),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='div_requestinvoice', to='hr.Division')),
                ('give_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_requestinvoice_givento', to='hr.Employee')),
                ('head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='head_requestinvoice', to='hr.Head')),
                ('office', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='office_requestinvoice', to='hr.Office')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reqestinvoice', to=settings.AUTH_USER_MODEL)),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unit_requestinvoice', to='hr.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='ReturnItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('collection_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReturnItemInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('returner_type', models.CharField(choices=[('Office', 'Office'), ('Employee', 'Employee'), ('Unit', 'Unit'), ('Head', 'Head'), ('Department', 'Department'), ('Division', 'Division')], max_length=30)),
                ('system_id', models.CharField(max_length=30)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('processedon', models.DateField()),
                ('note', models.CharField(blank=True, max_length=3000, null=True)),
                ('internal_reference', models.CharField(blank=True, max_length=35, null=True)),
                ('is_void', models.PositiveIntegerField(default=0)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dept_returninvoice', to='hr.Department')),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='div_returninvoice', to='hr.Division')),
                ('head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='head_returninvoice', to='hr.Head')),
                ('office', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='office_returninvoice', to='hr.Office')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_returninvoice', to=settings.AUTH_USER_MODEL)),
                ('return_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_returninvoice_returnedby', to='hr.Employee')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unit_returninvoice', to='hr.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='TechnicalService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrivedon', models.DateField()),
                ('comment', models.CharField(blank=True, max_length=20000, null=True)),
                ('action', models.CharField(choices=[('Repair', 'Repair'), ('Diagnose', 'Diagnose')], max_length=8)),
                ('monetary_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('manpower_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('new_status', models.CharField(blank=True, choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], default=None, max_length=30, null=True)),
                ('createdon', models.DateTimeField(auto_now_add=True)),
                ('updatedon', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomingitem_techservice', to='logistic.IncomingItem')),
                ('processedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_incomingitem_techservice', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WareHouseTally',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_status', models.CharField(choices=[('Unknown', 'Unknown'), ('New', 'New'), ('Used', 'Used'), ('Defective', 'Defective'), ('Disfunctional', 'Disfunctional'), ('Lost', 'Lost')], max_length=30)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=35)),
                ('for_month', models.DateField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_incomingitem', to='logistic.IncomingItem')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_store', to='inventory.Store')),
            ],
        ),
        migrations.AddField(
            model_name='returnitem',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returnitem_returninvoice', to='logistic.ReturnItemInvoice'),
        ),
        migrations.AddField(
            model_name='returnitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returnitem_outgoingitem', to='logistic.OutgoingItem'),
        ),
        migrations.AddField(
            model_name='returnitem',
            name='return_to_store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='returnitem_store', to='inventory.Store'),
        ),
        migrations.AddField(
            model_name='requesteditem',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesteditem_requestedinvoice', to='logistic.RequestInvoice'),
        ),
        migrations.AddField(
            model_name='requesteditem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_requestinvoice', to='inventory.Product'),
        ),
        migrations.AddField(
            model_name='provider',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provider_kinds', to='logistic.ProviderKind'),
        ),
        migrations.AddField(
            model_name='provider',
            name='processedby',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_provider', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='request_invoice',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_request', to='logistic.RequestInvoice'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_outgoinginvoice_transferedto', to='hr.Employee'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from_department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_dept_outgoinginvoice', to='hr.Department'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from_division',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_div_outgoinginvoice', to='hr.Division'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from_head',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_head_outgoinginvoice', to='hr.Head'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from_office',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_office_outgoinginvoice', to='hr.Office'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='transfered_from_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_unit_outgoinginvoice', to='hr.Unit'),
        ),
        migrations.AddField(
            model_name='outgoinginvoice',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unit_outgoinginvoice', to='hr.Unit'),
        ),
        migrations.AddField(
            model_name='incominginvoice',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incominginvoice_provider', to='logistic.Provider'),
        ),
    ]
