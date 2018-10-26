# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from mailer.simplemail import sendMessage
from datetime import date,timedelta #for checking renewal date range.

from tools.permissions import usersWithPermission
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from django.db.models import Sum

from logistic.models import ItemInStore,WareHouseTally,IncomingInvoice,RequestInvoice,OutgoingInvoice,ReturnItemInvoice

from app.conf import base as settings
import app.appsettings as appsettings
from django.db import connection
from tools.build_queries import dictfetchall


#@periodic_task(run_every=(crontab(minute='*/15')), name="warehouse_tally", ignore_result=True)

@periodic_task(run_every=(crontab(0, 0, day_of_month='1')), name="End of Month Store Items Inventory", ignore_result=True)
def endOfMonthInventory():
	'''
	Tally stores for warehouse operation. Please don't modify the timing nor call is directly from anywhere. Cellery will take care if it is running properly
	At the start of each month, it will run and count the number of each item that has remained in the store so we know with how many items we are starting the month
	'''

	#incase it is forced, cancel it unless it is day 1
	today=date.today()
	if today.day!=1:
		return False
		
	items_in_store=list(ItemInStore.objects.all().values('store_id','item_id','current_status','quantity'))

	if items_in_store:
		tally_items=[]
		today=date.today()
		year=today.year
		month=today.month
		if month==1:
			month=12
			year=year-1
		else:
			month=month-1

		for_month=date(year,month,1)
		for item in items_in_store:
			#item is dictionary now
			tally_item=WareHouseTally(store_id=item['store_id'],item_id=item['item_id'],current_status=item['current_status'],quantity=item['quantity'],for_month=for_month)
			tally_items.append(tally_item)
		WareHouseTally.objects.bulk_create(tally_items)
	
@periodic_task(run_every=(crontab(minute=0, hour='*/1')), name="clear_empty_packs", ignore_result=True)
def clearEmptyPacks():
	'''
	There could be empty invoices (Incoming,Return,Request,Outgoings)
	Note if an Oouting=Direct (processed request) is empty, set its Request to unprocessed

	Run every hour. Modiffy as necessary.

	Don't call directly from code; let Celery run it on its own
	'''
	
	try:
		ReturnItemInvoice.objects.filter(returnitem_returninvoice__isnull=True).distinct().delete()
		RequestInvoice.objects.filter(requesteditem_requestedinvoice__isnull=True).distinct().delete()
		RequestInvoice.objects.filter(outgoing_request__isnull=True,outgoing_request__direction='Direct').distinct().delete()
		OutgoingInvoice.objects.filter(outgoingitem_outgoinginvoice__isnull=True).distinct().delete()
		IncomingInvoice.objects.filter(incoming_item_invoice__isnull=True).distinct().delete()
	except:
		pass



@shared_task
def notifyExpiringItems():
	'''
	Get notification of expiration items sent to your email. Configure the time the expiration notification to be sent on the admin area
	'''
	filters={'item__product__kind':'Consumable'}

	today=date.today()
	
	expiry_date=today + timedelta(days=appsettings.APPSET_ALERT_EXPIRY_DAYS)

	filters['item__expire_on']=expiry_date

	
	items=ItemInStore.objects.filter(**filters).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','store__name').annotate(total_items=Sum('quantity')).order_by('store__name','item__product__name')

	
	items=list(items)


	if items:
		rows=''
		counter=1
		for item in items:
			rows=''.join([rows,'<tr><td>',str(counter),'</td><td>',item['item__product__name'],'/',item['item__manf__name'],'/',item['item__brand__name'],'</td><td>',item['store__name'],'</td><td>',item['total_items'],' ', item['item__product__measurement_unit'],'</td></tr>'])
			counter=counter + 1

		#get the file now and 

		email_message_template_file=''.join([settings.TEMPLATE_MESSAGES_DIR,'/en/expire_reminder.html'])

		with open(email_message_template_file) as data:
			email_msg=data.read()

		

		email_msg=email_msg.replace('{items}',rows).replace('{date}',expiry_date)


		

			
		logistic_people=usersWithPermission(['can_accept_expiry_items_notification'])
		
		if logistic_people:
			#we have people. just extract their emails here from the list
			emails=[x.get('email') for x in logistic_people]
			
			sendMessage(_('EmailSubjectExpiryItemsAlert'),email_msg,emails)

		return True


#@periodic_task(run_every=(crontab(minute='*/3')), name="low_instock_items", ignore_result=True)
@shared_task
def lowInStockItems():
	'''
	Returns items that are about to be finished or low in stock. Get notification via email. Set setting from admin area
	We care about Products here. So, we say Laptop 3, Water 100, Soup 900
	'''
	
	filters={}

	options="dic"

	items={}


	sql=""" SELECT 1 as id, SUM(logistic_iteminstore.quantity) AS total_items,inventory_product.name as pro_name,inventory_product.max_value as max_value,inventory_product.min_value as min_value,inventory_product.kind AS pro_kind,inventory_product.measurement_unit AS measure_unit
			FROM logistic_iteminstore,logistic_incomingitem,inventory_product
			WHERE logistic_iteminstore.item_id=logistic_incomingitem.id AND logistic_incomingitem.product_id=inventory_product.id GROUP BY pro_name,pro_kind,measure_unit  """


	#active_cropping=PlotCrop.objects.raw('SELECT id, COUNT(id) as total_farmers, SUM(quantity) as total_quantity FROM land_plotcrop WHERE still_open="YES" AND farmer_id IN (SELECT member_id FROM corporates_associationjoinedmember WHERE association_id=' + str(asso_id) + ') GROUP BY id')

	sql=  sql + ' HAVING (inventory_product.kind="Consumable" AND SUM(logistic_iteminstore.quantity)<=inventory_product.min_value ) OR '
	sql= sql + ' ( inventory_product.kind="Non-consumable" AND SUM(logistic_iteminstore.quantity)<=inventory_product.min_value)'


	sql=sql + " ORDER BY pro_name"

	try:
		with connection.cursor() as cursor:
			cursor.execute(sql)
			rows=dictfetchall(cursor)
			items=list(rows)
	except:
		items=[]

	


	
	if items:

		rows=''
		for item in items:
			needed=item['max_value'] - item['total_items']
			rows=''.join([rows,'<tr><td>',item['pro_name'],'</td><td>',str(item['total_items']), ' ',item['measure_unit'],'</td><td>',str(item['min_value']),'</td><td>',str(item['max_value']),'</td><td>', str(needed),'</td></tr>'])

		email_message_template_file=''.join([settings.TEMPLATE_MESSAGES_DIR,'/en/lowstock_reminder.html'])

		with open(email_message_template_file) as data:
			email_msg=data.read()

		

		email_msg=email_msg.replace('{items}',rows).replace('{date}',str(date.today()))



		logistic_people=usersWithPermission(['can_accept_low_stock_notification'])
		
		if logistic_people:
			#we have people. just extract their emails here from the list
			emails=[x.get('email') for x in logistic_people]
			
			sendMessage(_('EmailSubjectLowStockItemsAlert'),email_msg,emails)




	return True