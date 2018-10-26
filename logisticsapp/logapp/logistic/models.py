from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from inventory.models import Product,Brand,Manufacturer,Store
from app.conf import base as settings
from hr.models import Department, Division, Employee, Head, Office, Unit

class ProviderKind(models.Model):
	'''
	Kind of suppliers
	'''
	name=models.CharField(max_length=30,unique=True)
	processedby=models.ForeignKey(User,related_name='user_providerkind')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)


class Provider(models.Model):
	'''
	List of providers from whom items are bought. Providers could be shops or funders
	'''
	processedby=models.ForeignKey(User,related_name='user_provider')
	name=models.CharField(max_length=30)
	identification=models.CharField(max_length=30,blank=True,null=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	phone=models.CharField(max_length=13,blank=True,null=True)
	email=models.CharField(max_length=35,blank=True,null=True)
	www=models.CharField(max_length=255,blank=True,null=True)
	kind=models.ForeignKey(ProviderKind,related_name='provider_kinds')
	address=models.CharField(max_length=3000,null=True,blank=True)


class IncomingInvoice(models.Model):
	'''
	When items arrive (thru purchase etc), they are initiated here. An invoice can have multiple items that arrived under it
	'''
	
	processedby=models.ForeignKey(User,related_name='user_incominginvoice')
	system_id=models.CharField(max_length=30)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	processedon=models.DateField()
	
	provider=models.ForeignKey(Provider,related_name='incominginvoice_provider')
	provider_reference=models.CharField(max_length=35,blank=True,null=True)
	internal_reference=models.CharField(max_length=35,blank=True,null=True)


class IncomingItem(models.Model):
	'''
	Incoming Item stores items that arrival.

	Note: if user enters 30 computers, we add them all here individually so they can be tagged. That is applicable for Non-Consumable items only.
	'''
	
	invoice=models.ForeignKey(IncomingInvoice,related_name='incoming_item_invoice')
	product=models.ForeignKey(Product,related_name='incoming_item_product')
	brand=models.ForeignKey(Brand,related_name='incoming_item_brand')
	manf=models.ForeignKey(Manufacturer,related_name='incoming_item_manf')
	price=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	quantity=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	expire_on=models.DateField(null=True,blank=True)
	tag=models.CharField(max_length=35,null=True,blank=True)
	arrival_status=models.CharField(choices=settings.STATUS,max_length=30)
	processedby=models.ForeignKey(User,related_name='user_incomingitem')
	arrivedon=models.DateField()
	current_status=models.CharField(choices=settings.STATUS,max_length=30)
	collection_id=models.CharField(max_length=255,null=True,blank=True)
	placed_in_store=models.ForeignKey(Store,related_name='incomingitem_store')
	manf_serial=models.CharField(max_length=30,null=True,blank=True)
	institution_code=models.CharField(max_length=30,null=True,blank=True)
	
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	
class TechnicalService(models.Model):
	'''
	Service provided for the given item
	'''
	ACTION=(('Repair','Repair'),('Diagnose','Diagnose'))
	item=models.ForeignKey(IncomingItem,related_name='incomingitem_techservice')
	arrivedon=models.DateField()
	comment=models.CharField(max_length=20000,null=True,blank=True)
	action=models.CharField(choices=ACTION,max_length=8)
	processedby=models.ForeignKey(User,related_name='user_incomingitem_techservice')
	monetary_value=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	manpower_value=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	new_status=models.CharField(choices=settings.STATUS,max_length=30,default=None,null=True,blank=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)

class ItemInStore(models.Model):
	'''
	Items that are currently at a given store. We do delete records from the table as necessary
	'''
	store=models.ForeignKey(Store,related_name='iteminstore_store')
	item=models.ForeignKey(IncomingItem,related_name='iteminstore_incomingitem')
	current_status=models.CharField(choices=settings.STATUS,max_length=30)
	processedby=models.ForeignKey(User,related_name='user_iteminstore')
	quantity=models.DecimalField(max_digits=35,decimal_places=2,default=0)
	arrivedon=models.DateField()
	

class WareHouseTally(models.Model):
	'''
	At the end of each month, items that in store are counted and placed here automatically. This is not directly manipulated but from crontab only
	'''
	store=models.ForeignKey(Store,related_name='warehouse_store')
	item=models.ForeignKey(IncomingItem,related_name='warehouse_incomingitem')
	current_status=models.CharField(choices=settings.STATUS,max_length=30)
	quantity=models.DecimalField(max_digits=35,decimal_places=2,default=0)
	for_month=models.DateField()
	


class RequestInvoice(models.Model):
	'''
	April 24: Employees make a formal request for them or their unit/head etc. This is connected to OutgoingInvoice
	
	'''
	
	processedby=models.ForeignKey(User,related_name='user_reqestinvoice')
	give_to=models.ForeignKey(Employee,related_name='user_requestinvoice_givento',db_index=True,null=True)
	head=models.ForeignKey(Head,related_name='head_requestinvoice',db_index=True,null=True)
	department=models.ForeignKey(Department,related_name='dept_requestinvoice',db_index=True,null=True)
	division=models.ForeignKey(Division,related_name='div_requestinvoice',db_index=True,null=True)
	unit=models.ForeignKey(Unit,related_name='unit_requestinvoice',db_index=True,null=True)
	office=models.ForeignKey(Office,related_name='office_requestinvoice',db_index=True,null=True)
	receipent_type=models.CharField(max_length=30,choices=settings.RECEIPENT_TYPES)
	processedon=models.DateField()
	system_id=models.CharField(max_length=30)
	confirmed=models.PositiveIntegerField(default=0)

class RequestedItem(models.Model):
	'''
	Items that were requested. Here we care about product
	'''
	
	invoice=models.ForeignKey(RequestInvoice,related_name='requesteditem_requestedinvoice')
	product=models.ForeignKey(Product,related_name='product_requestinvoice')
	requested_quantity=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	


class OutgoingInvoice(models.Model):
	'''
	When items are distributed to employees, we store them here. Note during transfer, items work here.
	Direct means from store to employee. Transfer means one employee gives to another employee

	Changes: Jan 17, 2018: items can be placed in offices and those people in those offices are not responsible for them. As such,
	they are said to be given to an office, instead of an employee. Thus the model is changed to reflect those possiblities

	Note transfer can happen between any of those entities

	Future Changes: On April 25, I got copy of the Request form that affects Stocking Out. request_invoice is null for transfers
	'''
	DIRECTION=(('Direct',_('Direct')), ('Transfer',_('Transfer')))
	processedby=models.ForeignKey(User,related_name='user_outgoinginvoice')
	give_to=models.ForeignKey(Employee,related_name='user_outgoinginvoice_givento',db_index=True,null=True)
	head=models.ForeignKey(Head,related_name='head_outgoinginvoice',db_index=True,null=True)
	department=models.ForeignKey(Department,related_name='dept_outgoinginvoice',db_index=True,null=True)
	division=models.ForeignKey(Division,related_name='div_outgoinginvoice',db_index=True,null=True)
	unit=models.ForeignKey(Unit,related_name='unit_outgoinginvoice',db_index=True,null=True)
	office=models.ForeignKey(Office,related_name='office_outgoinginvoice',db_index=True,null=True)
	receipent_type=models.CharField(max_length=30,choices=settings.RECEIPENT_TYPES)
	request_invoice=models.OneToOneField(RequestInvoice,related_name='outgoing_request',db_index=True,null=True,default=None)

	system_id=models.CharField(max_length=30)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	processedon=models.DateField()
	note=models.CharField(max_length=3000,blank=True,null=True)
	internal_reference=models.CharField(max_length=35,blank=True,null=True)
	direction=models.CharField(max_length=30,choices=DIRECTION,default='Direct')
	transfered_from=models.ForeignKey(Employee,related_name='user_outgoinginvoice_transferedto',null=True,default=None)
	transfered_from_head=models.ForeignKey(Head,related_name='tr_head_outgoinginvoice',db_index=True,null=True)
	transfered_from_department=models.ForeignKey(Department,related_name='tr_dept_outgoinginvoice',db_index=True,null=True)
	transfered_from_division=models.ForeignKey(Division,related_name='tr_div_outgoinginvoice',db_index=True,null=True)
	transfered_from_unit=models.ForeignKey(Unit,related_name='tr_unit_outgoinginvoice',db_index=True,null=True)
	transfered_from_office=models.ForeignKey(Office,related_name='tr_office_outgoinginvoice',db_index=True,null=True)
	transfered_from_type=models.CharField(max_length=30,choices=settings.RECEIPENT_TYPES)

	is_void=models.PositiveIntegerField(default=0)


class OutgoingItem(models.Model):
	'''
	Items that were given in one outgoing invoice above
	'''
	OWNERSHIP_STATUS=((1,_('InPossession')), (2,_('Returned')) ,  (3,_('Lost')) ,  (4,_('Consumed')) , (5,_('Transfered')) )
	invoice=models.ForeignKey(OutgoingInvoice,related_name='outgoingitem_outgoinginvoice')
	item=models.ForeignKey(IncomingItem,related_name='outgoingitem_incomingitem')
	given_from_store=models.ForeignKey(Store,related_name='outgoingitem_store')
	given_status=models.CharField(max_length=30,choices=settings.STATUS)
	given_quantity=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	ownership_status=models.PositiveIntegerField(default=1,choices=OWNERSHIP_STATUS)
	collection_id=models.CharField(max_length=255,null=True,blank=True)
	processedby=models.ForeignKey(User,related_name='user_outgoingitem')
	transfered_item_id=models.PositiveIntegerField(default=0) #stores outgoingitem.id used during transfers only. We could have self-link OutgoingItem here but the db would be over loaded.
	arrived_to_store=models.DateField(default=None,null=True,blank=True)#during process request, when did the item arrive to the store anyway? Since ItemInStore is dynamic table, arrivedon column gets overriden. We use this value if the item is needed to be reversed back

class ReturnItemInvoice(models.Model):
	'''
	When employees returns an item, it is initiated here
	'''
	processedby=models.ForeignKey(User,related_name='user_returninvoice')
	return_by=models.ForeignKey(Employee,related_name='user_returninvoice_returnedby',db_index=True,null=True)
	head=models.ForeignKey(Head,related_name='head_returninvoice',db_index=True,null=True)
	department=models.ForeignKey(Department,related_name='dept_returninvoice',db_index=True,null=True)
	division=models.ForeignKey(Division,related_name='div_returninvoice',db_index=True,null=True)
	unit=models.ForeignKey(Unit,related_name='unit_returninvoice',db_index=True,null=True)
	office=models.ForeignKey(Office,related_name='office_returninvoice',db_index=True,null=True)
	returner_type=models.CharField(max_length=30,choices=settings.RECEIPENT_TYPES)
	
	system_id=models.CharField(max_length=30)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	processedon=models.DateField()
	note=models.CharField(max_length=3000,null=True,blank=True)
	internal_reference=models.CharField(max_length=35,blank=True,null=True)
	is_void=models.PositiveIntegerField(default=0)

class ReturnItem(models.Model):
	'''
	Items that were returned in one return invoice above
	'''
	invoice=models.ForeignKey(ReturnItemInvoice,related_name='returnitem_returninvoice')
	item=models.ForeignKey(OutgoingItem,related_name='returnitem_outgoingitem')
	return_to_store=models.ForeignKey(Store,related_name='returnitem_store',db_index=True,blank=True,null=True)
	return_status=models.CharField(max_length=30,choices=settings.STATUS)
	collection_id=models.CharField(max_length=255,null=True,blank=True)


class ItemUnconventionalHistory(models.Model):
	'''
	Typically, an item has a fixed or known history. It ARRIVES (incoming), distributes (Outgoing/Transfers) then is returned (Return)
	However, an item could also skip this steps cos it is lost. THen it joins the circle by being found. These are unconventional since
	they break down the expected life-circle of an item. However, they are still part of the item's identity. Thus, we keep them here.
	Note this does not have a direct interaction.
	'''
	item=models.ForeignKey(IncomingItem,related_name='unconventionalhistory_item')
	reportedon=models.DateField()
	factor=models.CharField(max_length=65)
	processedby=models.ForeignKey(User,related_name='user_unconventionalhistory')



	













