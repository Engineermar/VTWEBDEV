from hr.models import Head,Department,Division,Unit,Profession,Office,Notification
from logistic.models import ProviderKind
from inventory.models import Category,Product,Store
import os
from app.conf import base as settings
from datetime import date

import json

def addNotification(kind,user_id):
	'''
	On to-complete list. Not fully implementation. Each user has a set of notifications they are entitled to see. Here, we
	add notifications for hte specific user. We disable existing notifications first for the user so if there is no new notification on
	his/her next login, we don't bother himwith old notifications.

	@input: kind=>the kind of notification as determined by the calling module
	@input: user_id=> the user the notification affects
	
	Here,we are deleting old notifications; if we will follow social-media like notifications, remove the delete and use update() instead
	'''

	Notification.objects.filter(user_id=user_id,notify_kind=kind,is_counted=1).delete()

	notify=Notification(user_id=user_id,notify_kind=kind,is_counted=0,addedon=date.today())
	notify.save()

def publishHRStructureJSON(add_notify=True,user_id=0):
	'''
	Publish the HR structure of the company to a public JSON that can be viewed/consumed on a public API

	This is manually called by the user on demand or automatically when any of the HR elements is changed.

	@input add_notify: if true, notify users who haven't heard about hte change in teh hr structure except user_id
	@user_id if of hte user who made changes to the HR or manually called the publish

	When manually called,notificifaction is not added unless hte calling module/function sets add_notify=True for any reason. 
	'''
	
	#process

	#1. Get heads.
	data={}
	data['heads']=list(Head.objects.filter(active=1).values('id','name').order_by('name',))

	#2. Departments
	data['departments']=list(Department.objects.filter(active=1).values('id','name','head_id').order_by('name',))

	#divisions
	data['divisions']=list(Division.objects.filter(active=1).values('id','name','department_id').order_by('name',))

	#units
	data['units']=list(Unit.objects.filter(active=1).values('id','name','division_id').order_by('name',))

	#prfessions

	data['professions']=list(Profession.objects.filter(active=1).values('id','name').order_by('name',))

	#offices

	data['offices']=list(Office.objects.all().values('id','name','head_id','dept_id','division_id','unit_id').order_by('name'))


	hr_json_file=os.path.join(settings.BASE_DIR,'static/public/hr.json')

	with open(hr_json_file, 'w') as outfile:
		json.dump(data, outfile)

	#add notification?
	if add_notify:
		addNotification("1",user_id)
		


def publishCatalogStructureJSON(add_notify=True,user_id=0):
	
	'''
	Publish the Catalog  structure (Category=>Product,Stores and Supplier Kinds) of the company to a public JSON that can be viewed/consumed on a public API

	This is manually called by the user on demand or automatically when any of the Catalog elements is changed.

	@input add_notify: if true, notify users who haven't heard about hte change in teh catalog structure except user_id
	@user_id if of hte user who made changes to the catalog or manually called the publish

	When manually called,notificifaction is not added unless hte calling module/function sets add_notify=True for any reason. 
	'''

	#1. Get categories.
	data={}
	data['categories']=list(Category.objects.filter(active=1).values('id','name').order_by('name',))

	#2. products
	data['products']=list(Product.objects.filter(active=1).values('id','name','category_id','kind').order_by('name',))

	

	#stores

	data['stores']=list(Store.objects.all().values('id','name').order_by('name',))

	#supplier kinds
	data['supplier_kinds']=list(ProviderKind.objects.all().values('id','name').order_by('name',))



	catalog_json_file=os.path.join(settings.BASE_DIR,'static/public/items.json')

	with open(catalog_json_file, 'w') as outfile:
		json.dump(data, outfile)

	if add_notify:
		addNotification("2",user_id)	




		



