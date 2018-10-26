from app.conf import base as settings
from tools.formtools import csvFromUrlToNumbers
from dateutil import parser
from datetime import date,timedelta #for checking renewal date range.
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse


from hr.models import Employee,Head,Department,Division,Unit,Office

from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo

from logistic.models import IncomingInvoice, IncomingItem, ItemInStore, OutgoingItem, ReturnItem, TechnicalService, WareHouseTally

import app.appsettings as appsettings

from tools.build_quries import dateQueryBuilder, dictfetchall, distributionQueryBuilding, monthYearCompare, returnedItemsQueryBuilding, transferItemsQueryBuilding

from exporters.exporter import ExcelExporter
from django.db.models.functions import TruncMonth,TruncYear
from django.db import connection

from validation.validators import isDateValid
from django.db.models import When,CharField,Value,Case,F,OuterRef, Subquery,Count,Sum,Q
from django.db.models.functions import Concat,Coalesce
from tools.company import productInformation
from inventory.models import Product
from calendar import monthrange

if settings.RUNNING_DEVSERVER:
	
	from app.conf import development as web_settings
else:
	
	from app.conf import production as web_settings



class Financial(APIView):
	'''
	Financial report based on month/year and in between too.

	E.g. March, 2018 - March, 2019
	Product   Bought  Lost     Maintannce   Total Spending
	Laptop    9000     80rwf     90rwf         90
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['rpt_finreport'])

		if have_right:

			start_month=request.query_params.get('start_month','')
			start_year=request.query_params.get('start_year','')
			end_month=request.query_params.get('end_month','')
			end_year=request.query_params.get('end_year','')
	
			try:
				start_year=int(start_year)
			except:
				start_year=0

			try:
				start_month=int(start_month)
			except:
				start_month=0

			try:
				end_year=int(end_year)
			except:
				end_year=0

			try:
				end_month=int(end_month)
			except:
				end_month=0

			today=date.today()

			allowed_years=list(range(2012,today.year + 50))
			months=list(range(1,13))

			if start_year not in allowed_years:
				start_year=today.year

			if start_month not in months:
				start_month=today.month

			dt1=date(start_year,start_month,1)


			if end_year in allowed_years and end_month in months:
				
				dt2=date(end_year,end_month,1)
				if(dt1>dt2):
					#ignore second dates
					end_year=0

			filters=[]

			#filter_q.append(Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))

			if end_year==0:
				total_num_days=monthrange(start_year, start_month)
				dt2=date(start_year,start_month,total_num_days[1])
			filters.append(Q(arrivedon__range=[dt1,dt2]) | Q(incomingitem_techservice__arrivedon__range=[dt1,dt2]) | (Q(unconventionalhistory_item__reportedon__range=[dt1,dt2]) & Q(unconventionalhistory_item__factor='Lost') & Q(current_status='Lost')))
			'''
			filters.append(Q(incomingitem_techservice__arrivedon__range=[dt1,dt2]))
			filters.append(Q(unconventionalhistory_item__reportedon__range=[dt1,dt2]) & Q(unconventionalhistory_item__factor='Lost') & Q(current_status='Lost'))
			'''
			#report = DailyRecord.objects.annotate(total_manpower_spent=Sum(F('manpower_each_unitprice') * F('manpower_total'),output_field=DecimalField()),rec_name=Case(

			items=IncomingItem.objects.filter(*filters).values('product__name').annotate(total_purchased=Sum(F('quantity') * F('price')) ,total_on_lost=Coalesce(Sum('unconventionalhistory_item__item__price'),0),total_maintance_manpower=Coalesce(Sum('incomingitem_techservice__manpower_value'),0),total_maintance_items=Coalesce(Sum('incomingitem_techservice__monetary_value'),0) ).order_by('product__name')

			reply['start_date']=dt1
			reply['end_date']=dt2
			reply['detail']=list(items)
			
			status=200

			product_information=productInformation()

			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);


			

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)




class MonthlyReport(APIView):
	'''
	We generate general queries here per month. We accept a month + year then get previous month.

	e.g. User sends May, 2018. We calculate each category for April 2018 that was in store that month.

	Then we do te same for May, 2018
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,month,yr,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['rpt_monthlyreport'])

		if have_right:
			
			try:
				for_yr=int(yr)
			except:
				for_yr=0

			try:
				for_month=int(month)
			except:
				for_month=0

			today=date.today()

			allowed_years=list(range(2012,today.year + 1))
			months=list(range(1,13))

			if for_yr not in allowed_years:
				for_yr=today.year

			if for_month not in months:
				for_month=today.month

	

			
			pre_month=for_month-1
			pre_year=for_yr
			
			if pre_month==0:
				pre_month=12
				pre_year=for_yr-1

			#get items in store for premonth
			pre_month_filters={'for_month__year':pre_year,'for_month__month':pre_month}
			pre_month_items=list(WareHouseTally.objects.filter(**pre_month_filters).values('item__product__name','item__product__measurement_unit').annotate(total_items=Sum('quantity')).order_by('item__product__name'))


			#current month is purchases only so we filter Incoming items
			cur_month_filters={'arrivedon__year':for_yr,'arrivedon__month':for_month}
			cur_month_items=list(IncomingItem.objects.filter(**cur_month_filters).values('product__name','product__measurement_unit').distinct().annotate(total_items=Sum('iteminstore_incomingitem__quantity')).order_by('product__name'))
			
			#items that were distributed in current month
			cur_month_dist_filters={'invoice__processedon__year':for_yr,'invoice__processedon__month':for_month}
			dist_items=list(OutgoingItem.objects.filter(**cur_month_dist_filters).values('item__product__name','item__product__measurement_unit').annotate(total_items=Sum('given_quantity')).order_by('item__product__name'))




			products=[]
			if pre_month_items:
				for item in pre_month_items:
					pro_name=item['item__product__name']
					measure=item['item__product__measurement_unit']
					total=item['total_items']
					products.append({'pro_name':pro_name,'previus_total':total,'measure':measure,'now_total':0,'distributed':0})

			if cur_month_items:
				for item in cur_month_items:
					pro_name=item['product__name']
					measure=item['product__measurement_unit']
					total=item['total_items']
					#does the product exist in previous months report?
					add=True
					counter=0
					for product in products:
						if pro_name==product['pro_name']:
							products[counter]['now_total']=total
							add=False

							break
						counter=counter +1
					if add:
						products.append({'pro_name':pro_name,'previus_total':0,'measure':measure,'now_total':total,'distributed':0})

			if dist_items:
					for item in dist_items:
						pro_name=item['item__product__name']
						measure=item['item__product__measurement_unit']
						total=item['total_items']
						#does the product exist in previous months report?
						add=True
						counter=0
						for product in products:
							if pro_name==product['pro_name']:
								products[counter]['distributed']=total
								add=False

								break
							counter=counter +1
						if add:
							products.append({'pro_name':pro_name,'previus_total':0,'measure':measure,'now_total':0,'distributed':total})


			reply['detail']=products
			reply['pre_month']=pre_month 
			reply['pre_year']=pre_year
			reply['cur_month']=for_month
			reply['cur_year']=for_yr
			status=200
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);


			

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)




class InStore(APIView):
	'''
	Do instore report
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_instore'])

		if have_right:
			report_type=request.query_params.get('option','q').strip()
			if str(report_type).lower() not in ['d','q','s']:
				report_type='q';

			output_option=request.query_params.get('output','w').strip().lower()

			if output_option not in ['w','x','p']:
				output_option='w'

			products=request.query_params.get('products','') #csv
			stores=request.query_params.get('stores','') #csv
			kinds=request.query_params.get('kinds','').strip().capitalize()
			item_status=request.query_params.get('status','').strip()
			#not paged. Let DataTable manage it on the front end.
			filters={}
			if kinds in ['Consumable','Non-consumable']:
				filters['item__product__kind']=kinds

			stores=csvFromUrlToNumbers(stores)
			if stores:
				filters['store_id__in']=stores

			products=csvFromUrlToNumbers(products)
			if products:
				filters['item__product_id__in']=products

			item_status=csvFromUrlToNumbers(item_status,num='str')

			if item_status:
				filters['current_status__in']=item_status

			if report_type=='d':
				items=ItemInStore.objects.filter(**filters).values('quantity','item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price','item__expire_on','item__tag','current_status','store__name','item__institution_code','item__manf_serial').order_by('item__product__name',)
			elif report_type=='q':
				items=ItemInStore.objects.filter(**filters).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','store__name').annotate(total_items=Sum('quantity')).order_by('store__name','item__product__name')
			elif report_type=='s':
				items=ItemInStore.objects.filter(**filters).values('item__product__name','item__product__measurement_unit').annotate(total_items=Sum('quantity')).order_by('item__product__name')
			items=list(items)
			reply['report_type']=report_type
			reply['output_option']=output_option
			reply['items']=items
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);


			

			status=200



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class StockedIn(APIView):
	'''
	What did we stock in?
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['rpt_stockins'])

		if have_right:

			filters={}

			
			option=request.query_params.get('option','q').strip().lower()
			suppliers=request.query_params.get('suppliers','').strip() #csv list
			kind=request.query_params.get('kinds','').strip() #csv list of nature of the invocie (unded, purchased)
			supplier_kinds=request.query_params.get('supplier_kinds','').strip()
			system_id=request.query_params.get('system_id','').strip()
			provider_reference=request.query_params.get('supplier_ref','').strip()
			internal_reference=request.query_params.get('internal_ref','').strip()
			
			stocked_on1=request.query_params.get('done_date1')
			stocked_on2=request.query_params.get('done_date2')
			stocked_portion_option=request.query_params.get('done_portion','y')
			stocked_option=request.query_params.get('done_date_option','e')
			'''
			totalcost_min=request.query_params.get('value_min')
			totalcost_max=request.query_params.get('value_max')
			totalcost_option=request.query_params.get('value_option','e')
			value_compare=numericalQueryBuilder('total_price',totalcost_min,totalcost_max,totalcost_option)
			if value_compare:

				filters[value_compare[0]]=value_compare[1]
			'''

			products=request.query_params.get('products','').strip()
			
			stockedon_compare=dateQueryBuilder('invoice__processedon',stocked_portion_option,stocked_on1,stocked_on2,stocked_option)

			products=csvFromUrlToNumbers(products,num='int',ignore_zero=True)

			supplier_kinds=csvFromUrlToNumbers(supplier_kinds,num='str')

			if option not in ['q','d','s']:
				option='q'

			if supplier_kinds:
				filters['invoice__provider__kind__in']=supplier_kinds

			

			if products:
				filters['product_id__in']=products

			suppliers=csvFromUrlToNumbers(suppliers,ignore_zero=True)

			if suppliers:
				filters['invoice__provider_id__in']=suppliers

		

			if system_id:
				filters['invoice__system_id']=system_id

			if provider_reference:
				filters['invoice__provider_reference']=provider_reference

			if  internal_reference:
				filters['invoice__internal_reference']=internal_reference

			if stockedon_compare:
				filters[stockedon_compare[0]]=stockedon_compare[1]
				#for month equal, we have additional data.
				if len(stockedon_compare)==4:
					filters[stockedon_compare[2]]=stockedon_compare[3]



			if option=='d':

				records=IncomingItem.objects.filter(**filters).values('id','invoice__system_id','invoice__provider__name','invoice__processedon','product__name','brand__name','manf__name','invoice_id','quantity','price').order_by('product__name',)
			elif option=='q':
				records=IncomingItem.objects.filter(**filters).values('product__name','brand__name','manf__name').annotate(total=Sum('quantity')).order_by('product__name',)
			else:
				records=IncomingItem.objects.filter(**filters).values('product__name').annotate(total=Sum('quantity')).order_by('product__name',)
			
			
			reply['detail']=list(records)
			status=200
			reply['option']=option
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);

			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ExpiringItems(APIView):
	'''
	List of items that might expire on a given time. Accept a time period here instead of dates:

	today
	tomorrow
	inthreedays
	inaweek
	intwoweeks
	inthreeweeks
	inamonth
	inamonthhalf
	intwomonths
	inthreemonths
	insixmonths

	==past:

	yesterday
	lastweek
	lasttwoweeks
	lastmonth

	Update: No Erick's recommendation on Jan 21, 1AM, we are accepting date instead. Look for Jan 21 back up for a working example of the previous method
	If no date is provided or is invalid format, we assume it is for a month


	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_expiring_items'])

		if have_right:
			cal_option=request.query_params.get('cal_option','').strip().lower() #date, if given
			output_option=request.query_params.get('output','w').strip().lower()
		
			report_type=request.query_params.get('option','q').strip().lower()
			if report_type not in ['d','q']:
				report_type='q'
			

			products=request.query_params.get('products','') #:
			stores=request.query_params.get('stores','') #csv
			
			filters={'item__product__kind':'Consumable'}

			stores=csvFromUrlToNumbers(stores)
			if stores:
				filters['store_id__in']=stores

			products=csvFromUrlToNumbers(products)
			if products:
				filters['item__product_id__in']=products

			today=date.today()
			expiry_date=today

			if not isDateValid(cal_option,criteria='any',max_age=0,min_age=0):
				#expiray date is invalid. So, lets show items that will expire in a month based on settings.
				expiry_date=today + timedelta(days=appsettings.APPSET_DEFAULT_EXPIRYDAYS)

				reply['tip']=_('TipRptExpiryDateInvalid') % {'days':str(appsettings.APPSET_DEFAULT_EXPIRYDAYS)}
				
			else:
				#DATE GIVEN. So e.g. if selected date is 2018-09-15, go back 5 days and go forward 15 days. So we get items
				#that expire between 2018-09-10 and 2018-09-30
				expiry_date=parser.parse(str(cal_option)).date()

			backword_days=expiry_date - timedelta(days=appsettings.APPSET_EXPIRAYDATE_BACKWORDDAYS)
			forword_days=expiry_date + timedelta(days=appsettings.APPSET_EXPIRAYDATE_FORWARDDAYS)
			expire_options=[backword_days,forword_days]
				




			filters['item__expire_on__range']=expire_options


			#now build the query.

			if report_type=='d':
				items=ItemInStore.objects.filter(**filters).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price','item__expire_on','quantity','store__name').order_by('item__product__name',)
			elif report_type=='q':
				items=ItemInStore.objects.filter(**filters).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','store__name').annotate(total_items=Sum('quantity')).order_by('store__name','item__product__name')

			
			items=list(items)
			reply['items']=items

			

			
			reply['report_type']=report_type
			reply['output_option']=output_option
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			
			status=200



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class FinishingProducts(APIView):
	'''
	Returns items that are about to be finished. There is a setting for consumable and non-consumable for their threshold.
	We care about Products here. So, we say Laptop 3, Water 100, Soup 900
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_finishing_items'])

		if have_right:
			kind=request.query_params.get('kind','').strip().capitalize() #consumable or non consumable
			output_option=request.query_params.get('output','w').strip().lower()

			filters={}

			options="dic"

			items={}

	
			sql=""" SELECT 1 as id, SUM(logistic_iteminstore.quantity) AS total_items,inventory_product.name as pro_name,inventory_product.max_value as max_value,inventory_product.min_value as min_value,inventory_product.kind AS pro_kind,inventory_product.measurement_unit AS measure_unit
					FROM logistic_iteminstore,logistic_incomingitem,inventory_product
					WHERE logistic_iteminstore.item_id=logistic_incomingitem.id AND logistic_incomingitem.product_id=inventory_product.id GROUP BY pro_name,pro_kind,measure_unit  """


			#active_cropping=PlotCrop.objects.raw('SELECT id, COUNT(id) as total_farmers, SUM(quantity) as total_quantity FROM land_plotcrop WHERE still_open="YES" AND farmer_id IN (SELECT member_id FROM corporates_associationjoinedmember WHERE association_id=' + str(asso_id) + ') GROUP BY id')

			if kind=='Consumable':
				
				sql=  sql + ' HAVING (inventory_product.kind="Consumable" AND SUM(logistic_iteminstore.quantity)<=inventory_product.min_value )'

			elif kind=='Non-consumable':

				sql= sql + ' HAVING ( inventory_product.kind="Non-consumable" AND SUM(logistic_iteminstore.quantity)<=inventory_product.min_value)'
				
			else:

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


			reply['items']=items
			reply['output_option']=output_option
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);


			if output_option=='x':
				#output to excel. So send file here. Create thefile the force download it
				
				export=ExcelExporter()
				fileName=export.export(request.user.username, items, 'finishing_war',None )
				
				reply['file']=web_settings.WEB_ADDRESS + fileName


			status=200

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ItemHistory(APIView):
	'''
	View history of an item. We serve one kind of view but they can switch the display to their liking. Note that this is non-consumable only
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['rpt_item_history'])

		if have_right:
			tag=request.query_params.get('tag','').strip() #the actual vaue
			level=request.query_params.get('level','').strip() #what to include in the report
			searchby=request.query_params.get('searchby','').strip().lower()

			#level 1 =>Directly Taken
			#level 2 =>Thru Transfers
			#level 3 =>Returns
			#level 4=> All/Chain

			if level not in ['1','2','3','4','5']:
				level='1'

			if searchby not in ['tag','rlrc','manf']:
				searchby='rlrc'



			level=int(level)

			filters={}

			locate_item_by={'product__kind':'Non-consumable'}

			if searchby=='tag':
				locate_item_by['tag']=tag
			elif searchby=='rlrc':
				locate_item_by['institution_code']=tag
			else:
				locate_item_by['manf_serial']=tag

		
			try:
				
				item=IncomingItem.objects.values('id','product__asset_code','institution_code','manf_serial','product__kind','placed_in_store__name','arrivedon','brand__name','manf__name','price','tag','current_status','arrival_status','processedby__username','product__name','product__category__name','invoice__system_id','invoice__internal_reference','invoice_id','invoice__provider__name','invoice__processedon','product__depreciation_method','product__lasts_for_years').get(**locate_item_by)
				#item existing. Now based on level get additional data

				reply['item']=item

				item_id=item['id']

				if level==1:
					#get Directly Taken History Only
					history = OutgoingItem.objects.annotate(
						reciepent_name=Case(

						When(invoice__receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
						When(invoice__receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
						When(invoice__receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
						When(invoice__receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
						When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
						When(invoice__receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__give_to_id')).values('full_name'))),
						

						output_field=CharField())).filter(item_id=item_id,invoice__direction='Direct').values('invoice__system_id','invoice__processedon','invoice__internal_reference','reciepent_name','given_status','given_from_store__name','invoice__receipent_type').order_by('-id',)

					

				elif level==2:
					#got thru transfer
					history = OutgoingItem.objects.annotate(
						reciepent_name=Case(

						When(invoice__receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
						When(invoice__receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
						When(invoice__receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
						When(invoice__receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
						When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
						When(invoice__receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__give_to_id')).values('full_name'))),
						

						output_field=CharField()),

						transfered_from_name=Case(

						When(invoice__transfered_from_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__transfered_from_head_id')).values('name',))),
						When(invoice__transfered_from_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__transfered_from_department_id')).values('full_name'))),
						When(invoice__transfered_from_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__transfered_from_division_id')).values('full_name'))),
						When(invoice__transfered_from_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__transfered_from_unit_id')).values('full_name'))),
						When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__transfered_from_office_id')).values('name'))),
						When(invoice__transfered_from_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__transfered_from_id')).values('full_name'))),
						
						output_field=CharField())



						).filter(item_id=item_id,invoice__direction='Transfer').values('invoice__system_id','invoice__processedon','invoice__internal_reference','reciepent_name','given_status','given_from_store__name','invoice__receipent_type','invoice__transfered_from_type','transfered_from_name').order_by('-id',)
					
				elif level==3:
					#returns he did

					history = ReturnItem.objects.annotate(
						reciepent_name=Case(

						When(invoice__returner_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
						When(invoice__returner_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
						When(invoice__returner_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
						When(invoice__returner_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
						When(invoice__returner_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
						When(invoice__returner_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__return_by_id')).values('full_name'))),
						

						output_field=CharField())).filter(item__item_id=item_id).values('invoice__system_id','invoice__processedon','invoice__internal_reference','reciepent_name','return_status','item__given_status','invoice__returner_type').order_by('-id',)
		
				elif level==4:
					#late addition. Maintenance



					history = TechnicalService.objects.filter(item_id=item_id).values('action','arrivedon','monetary_value','manpower_value','new_status','processedby__first_name','processedby__last_name').order_by('-id',)
					
				elif level==5:
					#chained. Union them here
					sql=""" SELECT "Given" as action, logistic_outgoinginvoice.system_id as system_id, logistic_outgoinginvoice.processedon as processedon, 
							logistic_outgoinginvoice.receipent_type as receipent_kind,
							logistic_outgoinginvoice.internal_reference as internal_reference,
							  logistic_outgoingitem.given_status as item_info_status,
							 "N/A"  as return_status,
							 inventory_store.name as store_name,
	                         "N/A" as transfered_from_type,
	                         "N/A" as transfered_from_name,

							CASE 
							WHEN logistic_outgoinginvoice.receipent_type = 'Head' THEN (SELECT U0.name FROM hr_head as U0 WHERE U0.id = (logistic_outgoinginvoice.head_id))
							WHEN logistic_outgoinginvoice.receipent_type = 'Department' THEN (SELECT CONCAT_WS('-', U1.name, CONCAT_WS('-' ,'-' , U0.name)) FROM hr_department U0 INNER JOIN hr_head U1 ON (U0.head_id = U1.id) WHERE U0.id = (logistic_outgoinginvoice.department_id)) 

							WHEN logistic_outgoinginvoice.receipent_type = 'Division' THEN (SELECT CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-' , U0.name)))) FROM hr_division U0 INNER JOIN hr_department U1 ON (U0.department_id = U1.id) INNER JOIN hr_head U2 ON (U1.head_id = U2.id) WHERE U0.id = (logistic_outgoinginvoice.division_id))

							WHEN logistic_outgoinginvoice.receipent_type = 'Employee' THEN (SELECT CONCAT_WS('-',auth_user.last_name,auth_user.first_name) FROM hr_employee INNER JOIN auth_user ON hr_employee.user_id=auth_user.id WHERE hr_employee.id=logistic_outgoinginvoice.give_to_id)

							WHEN logistic_outgoinginvoice.receipent_type = 'Unit' THEN (SELECT CONCAT_WS(',', U3.name, CONCAT_WS('-' , CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-', U0.name)))))) FROM hr_unit U0 INNER JOIN hr_division U1 ON (U0.division_id = U1.id) INNER JOIN hr_department U2 ON (U1.department_id = U2.id) INNER JOIN hr_head U3 ON (U2.head_id = U3.id) WHERE U0.id = (logistic_outgoinginvoice.unit_id)) 

							WHEN logistic_outgoinginvoice.receipent_type = 'Office' THEN (SELECT U4.name FROM hr_office as U4 WHERE U4.id = (logistic_outgoinginvoice.office_id))

							END as full_name

							FROM logistic_outgoingitem INNER JOIN logistic_outgoinginvoice ON (logistic_outgoingitem.invoice_id = logistic_outgoinginvoice.id)  INNER JOIN inventory_store ON (logistic_outgoingitem.given_from_store_id = inventory_store.id) WHERE (logistic_outgoingitem.item_id = {0} AND logistic_outgoinginvoice.direction = "Direct")

							UNION ALL 

							SELECT "Transfered" as action, logistic_outgoinginvoice.system_id as system_id, logistic_outgoinginvoice.processedon as processedon, 
							logistic_outgoinginvoice.receipent_type as receipent_kind,
							logistic_outgoinginvoice.internal_reference as internal_reference,
						    logistic_outgoingitem.given_status as item_info_status,
						 	"N/A"  as return_status,
						    inventory_store.name as store_name,
							logistic_outgoinginvoice.transfered_from_type as transfered_from_type,
							                         

							CASE 
							WHEN logistic_outgoinginvoice.receipent_type = 'Head' THEN (SELECT U0.name FROM hr_head as U0 WHERE U0.id = (logistic_outgoinginvoice.head_id))
							WHEN logistic_outgoinginvoice.receipent_type = 'Department' THEN (SELECT CONCAT_WS('-', U1.name, CONCAT_WS('-' ,'-' , U0.name)) FROM hr_department U0 INNER JOIN hr_head U1 ON (U0.head_id = U1.id) WHERE U0.id = (logistic_outgoinginvoice.department_id)) 

							WHEN logistic_outgoinginvoice.receipent_type = 'Division' THEN (SELECT CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-' , U0.name)))) FROM hr_division U0 INNER JOIN hr_department U1 ON (U0.department_id = U1.id) INNER JOIN hr_head U2 ON (U1.head_id = U2.id) WHERE U0.id = (logistic_outgoinginvoice.division_id))

							WHEN logistic_outgoinginvoice.receipent_type = 'Employee' THEN (SELECT CONCAT_WS('-',auth_user.last_name,auth_user.first_name) FROM hr_employee INNER JOIN auth_user ON hr_employee.user_id=auth_user.id WHERE hr_employee.id=logistic_outgoinginvoice.give_to_id)

							WHEN logistic_outgoinginvoice.receipent_type = 'Unit' THEN (SELECT CONCAT_WS(',', U3.name, CONCAT_WS('-' , CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-', U0.name)))))) FROM hr_unit U0 INNER JOIN hr_division U1 ON (U0.division_id = U1.id) INNER JOIN hr_department U2 ON (U1.department_id = U2.id) INNER JOIN hr_head U3 ON (U2.head_id = U3.id) WHERE U0.id = (logistic_outgoinginvoice.unit_id)) 

							WHEN logistic_outgoinginvoice.receipent_type = 'Office' THEN (SELECT U4.name FROM hr_office as U4 WHERE U4.id = (logistic_outgoinginvoice.office_id))
							
							END as full_name,
							    
							CASE 
							WHEN logistic_outgoinginvoice.transfered_from_type = 'Head' THEN (SELECT U0.name FROM hr_head as U0 WHERE U0.id = (logistic_outgoinginvoice.transfered_from_head_id))
							WHEN logistic_outgoinginvoice.transfered_from_type = 'Department' THEN (SELECT CONCAT_WS('-', U1.name, CONCAT_WS('-' ,'-' , U0.name)) FROM hr_department U0 INNER JOIN hr_head U1 ON (U0.head_id = U1.id) WHERE U0.id = (logistic_outgoinginvoice.transfered_from_department_id)) 

							WHEN logistic_outgoinginvoice.transfered_from_type = 'Division' THEN (SELECT CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-' , U0.name)))) FROM hr_division U0 INNER JOIN hr_department U1 ON (U0.department_id = U1.id) INNER JOIN hr_head U2 ON (U1.head_id = U2.id) WHERE U0.id = (logistic_outgoinginvoice.transfered_from_division_id))

							WHEN logistic_outgoinginvoice.transfered_from_type = 'Employee' THEN (SELECT CONCAT_WS('-',auth_user.last_name,auth_user.first_name) FROM hr_employee INNER JOIN auth_user ON hr_employee.user_id=auth_user.id WHERE hr_employee.id=logistic_outgoinginvoice.transfered_from_id)

							WHEN logistic_outgoinginvoice.transfered_from_type = 'Unit' THEN (SELECT CONCAT_WS(',', U3.name, CONCAT_WS('-' , CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-', U0.name)))))) FROM hr_unit U0 INNER JOIN hr_division U1 ON (U0.division_id = U1.id) INNER JOIN hr_department U2 ON (U1.department_id = U2.id) INNER JOIN hr_head U3 ON (U2.head_id = U3.id) WHERE U0.id = (logistic_outgoinginvoice.transfered_from_unit_id)) 

							WHEN logistic_outgoinginvoice.transfered_from_type  = 'Office' THEN (SELECT U4.name FROM hr_office as U4 WHERE U4.id = (logistic_outgoinginvoice.transfered_from_office_id))

							END as transfered_from_name

							FROM logistic_outgoingitem INNER JOIN logistic_outgoinginvoice ON (logistic_outgoingitem.invoice_id = logistic_outgoinginvoice.id)  INNER JOIN inventory_store ON (logistic_outgoingitem.given_from_store_id = inventory_store.id) WHERE (logistic_outgoingitem.item_id = {1} AND logistic_outgoinginvoice.direction = "Transfer")						 
							 
							UNION ALL

							 SELECT "Maintenance" as action,' ' as systemid,
							 logistic_technicalservice.arrivedon as processedon,
							 " " as internal_reference,
							 CONCAT_WS(',', auth_user.last_name,auth_user.first_name) as full_name,
							 " " as receipent_kind,
							 new_status as item_info_status,
							 " " as return_status,
							 " " as transfered_from_name,
							 " " as transfered_from_type,
							 " "  as store_name

							 FROM logistic_technicalservice

							 INNER JOIN auth_user ON auth_user.id=logistic_technicalservice.processedby_id

							  WHERE (logistic_technicalservice.item_id = {2}) 						

							 UNION ALL

							 SELECT factor as action,' ' as systemid,
							 logistic_itemunconventionalhistory.reportedon as processedon,
							 " " as internal_reference,
							 " " as full_name,
							 " " as receipent_kind,
							 " " as item_info_status,
							 "N/A" as return_status,
							 "N/A" as transfered_from_name,
							 "N/A" as transfered_from_type,
							 "N/A"  as store_name

							 FROM logistic_itemunconventionalhistory WHERE (logistic_itemunconventionalhistory.item_id = {3}) 

							

							UNION ALL


							SELECT "Returned" as action, logistic_returniteminvoice.system_id as system_id, logistic_returniteminvoice.processedon as processedon, 
							logistic_returniteminvoice.returner_type as receipent_kind,
							logistic_returniteminvoice.internal_reference as internal_reference,
							  logistic_outgoingitem.given_status as item_info_status,
							 logistic_returnitem.return_status  as return_status,
							 "N/A" as store_name,
	                         "N/A" as transfered_from_type,
	                         "N/A" as transfered_from_name,
	                         

							 CASE 
							WHEN logistic_returniteminvoice.returner_type = 'Head' THEN (SELECT U0.name FROM hr_head as U0 WHERE U0.id = (logistic_returniteminvoice.head_id))
							WHEN logistic_returniteminvoice.returner_type = 'Department' THEN (SELECT CONCAT_WS('-', U1.name, CONCAT_WS('-' ,'-' , U0.name)) FROM hr_department U0 INNER JOIN hr_head U1 ON (U0.head_id = U1.id) WHERE U0.id = (logistic_returniteminvoice.department_id)) 

							WHEN logistic_returniteminvoice.returner_type = 'Division' THEN (SELECT CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-' , U0.name)))) FROM hr_division U0 INNER JOIN hr_department U1 ON (U0.department_id = U1.id) INNER JOIN hr_head U2 ON (U1.head_id = U2.id) WHERE U0.id = (logistic_returniteminvoice.division_id))

							WHEN logistic_returniteminvoice.returner_type = 'Employee' THEN (SELECT CONCAT_WS('-',auth_user.last_name,auth_user.first_name) FROM hr_employee INNER JOIN auth_user ON hr_employee.user_id=auth_user.id WHERE hr_employee.id=logistic_returniteminvoice.return_by_id)

							WHEN logistic_returniteminvoice.returner_type = 'Unit' THEN (SELECT CONCAT_WS(',', U3.name, CONCAT_WS('-' , CONCAT_WS('-', U2.name, CONCAT_WS('-' , CONCAT_WS('-', U1.name, CONCAT_WS('-', U0.name)))))) FROM hr_unit U0 INNER JOIN hr_division U1 ON (U0.division_id = U1.id) INNER JOIN hr_department U2 ON (U1.department_id = U2.id) INNER JOIN hr_head U3 ON (U2.head_id = U3.id) WHERE U0.id = (logistic_returniteminvoice.unit_id)) 

							WHEN logistic_returniteminvoice.returner_type = 'Office' THEN (SELECT U4.name FROM hr_office as U4 WHERE U4.id = (logistic_returniteminvoice.office_id))
							END as full_name

							FROM logistic_returnitem INNER JOIN logistic_returniteminvoice ON (logistic_returnitem.invoice_id = logistic_returniteminvoice.id) INNER JOIN logistic_outgoingitem ON (logistic_returnitem.item_id=logistic_outgoingitem.id) WHERE (logistic_outgoingitem.item_id = {4})
													 		
							ORDER BY processedon DESC """.format(item_id,item_id,item_id,item_id,item_id)

			

				if level<5:
					history=list(history)

				else:
					
					with connection.cursor() as cursor:
						cursor.execute(sql)
						rows=dictfetchall(cursor)
						history=list(rows)
					
						

				product_information=productInformation()
				reply['software_name']=product_information['product_name']

				reply['company_name']=product_information['company_name']

				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				reply['level']=level
				reply['history']=history
				status=200

			
			except:
				reply['detail']=_('ErrorItemMissing')
				history=[]
				status=400
		

		


		else:
			reply['detail']=_('NoRight')
			status=400


		return JsonResponse(reply,status=status)

class ItemsInMyHand(APIView):
	'''
	logged in user to see items in his/her possession. Just non-consuambles

	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		'''
		e_kind=Employee, Head=>Unit
		e_id=>id of the entity
		'''

		reply={}
		status=200

		report_type=request.query_params.get('report_type','q').strip().lower()

		filters={}
		

		if report_type=='q':
			#generate quantified report
	
			filters=distributionQueryBuilding('Employee', request.user.id,'Non-consumable','inhand') #this is dictionary
			items=list(OutgoingItem.objects.filter(**filters).values('item__product__name').annotate(quantity=Sum('given_quantity'),cost=Sum('item__price')).order_by('item__product__name',))

		else:

			filters=distributionQueryBuilding('Employee', request.user.id, 'Non-consumable','inhand') #this is dictionary
			items=list(OutgoingItem.objects.filter(**filters).values('invoice__system_id','item__institution_code','item__manf__name',  'invoice__internal_reference','item__product__name','item__brand__name','item__manf__name','item__price','given_quantity','given_status','invoice__processedon').order_by('item__product__name',))
				

		reply['report_type']=report_type
		product_information=productInformation()
		reply['software_name']=product_information['product_name']

		reply['company_name']=product_information['company_name']

		reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
		
		reply['items']=items

		status=200



		return JsonResponse(reply,status=status)	

class EntityHistory(APIView):
	'''
	See items employee has taken always or just currently

	UPDATE: After Louis said items can be owned by an org structure, the above was renamed to EntityHistory from EmployeeHistory.

	urls.py was as well updated.

	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,e_kind,e_id,format=None):
		'''
		e_kind=Employee, Head=>Unit
		e_id=>id of the entity
		'''

		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['rpt_entity_history'])

		if have_right:

			
			rpt_option=request.query_params.get('rpt_option','').strip() #what kind of report?
			item_filter=request.query_params.get('item_filter','Non-consumable').strip().capitalize() # Non-cons or cons
			output_option=request.query_params.get('output','').strip().capitalize()
			report_type=request.query_params.get('report_type','q').strip().lower()

			filters={}
			

			if report_type=='q':
				#generate quantified report
				if rpt_option in ['inhand','inhand-direct','inhand-transfered','lost']:

					filters=distributionQueryBuilding(e_kind, e_id, item_filter,rpt_option) #this is dictionary
					items=list(OutgoingItem.objects.filter(**filters).values('item__product__name').annotate(quantity=Sum('given_quantity'),cost=Sum('item__price')).order_by('item__product__name',))
					report_option='og'
				elif rpt_option=='returned':
					#returning items
					filters=returnedItemsQueryBuilding(e_kind,e_id)
					report_option='rt'
					items=list(ReturnItem.objects.filter(**filters).values('item__item__product__name').annotate(quantity=Count('id'),cost=Sum('item__item__price')).order_by('item__item__product__name',))
				elif rpt_option=='transfered':
					#transfered items to others
					filters=transferItemsQueryBuilding(e_kind, e_id)
					items=list(OutgoingItem.objects.filter(**filters).values('item__product__name').annotate(quantity=Sum('given_quantity'),cost=Sum('item__price')).order_by('item__product__name',))
					report_option='og'



			else:
				if rpt_option in ['inhand','inhand-direct','inhand-transfered','lost']:

					filters=distributionQueryBuilding(e_kind, e_id, item_filter,rpt_option) #this is dictionary
					items=list(OutgoingItem.objects.filter(**filters).values('invoice__system_id','item__institution_code','item__manf__name',  'invoice__internal_reference','item__product__name','item__brand__name','item__manf__name','item__price','given_quantity','given_status','invoice__processedon').order_by('item__product__name',))
					report_option='og'
				elif rpt_option=='returned':
					#returning items
					filters=returnedItemsQueryBuilding(e_kind,e_id)
					report_option='rt'
					items=list(ReturnItem.objects.filter(**filters).values('invoice__system_id','invoice__processedon','item__item__institution_code','item__item__manf_serial', 'item__item__product__name','item__item__price','item__item__brand__name','item__item__manf__name','item__given_status','return_status','invoice__processedon').order_by('item__item__product__name',))
				elif rpt_option=='transfered':
					#transfered items to others
					filters=transferItemsQueryBuilding(e_kind, e_id)
					items=list(OutgoingItem.objects.filter(**filters).values('invoice__system_id','invoice__internal_reference','item__institution_code','item__manf_serial',  'item__product__name','item__brand__name','item__manf__name','item__price','given_status','invoice__processedon').order_by('item__product__name',))
					report_option='og'

			reply['rpt_option']=report_option
			reply['report_type']=report_type

			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			
			reply['items']=items

			status=200


		

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	


class Suppliers(APIView):
	'''
	Suppliers report. We pass ids of suppliers here in csv format. If no supplier id selected, we go ahead.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_suppliers'])

		if have_right:

			
			
			item_filter=request.query_params.get('item_filter','Non-consumable').strip().capitalize() # Non-cons or cons
			suppliers=request.query_params.get('suppliers','').strip()
			output_option=request.query_params.get('output','').strip().capitalize()
			report_type=request.query_params.get('report_type','q').strip().lower()
			products=request.query_params.get('products','').strip()

			filters={}

			suppliers=csvFromUrlToNumbers(suppliers)
			products=csvFromUrlToNumbers(products)

			if suppliers:
				filters['invoice__provider_id__in']=suppliers

			if products:
				filters['product_id__in']=products

			if item_filter:
				filters['product__kind']=item_filter
			

			if report_type=='q':
				#generate quantified report
				items=list(IncomingItem.objects.filter(**filters).values('product__name','invoice__provider__name','invoice__provider__identification','product__measurement_unit').annotate(total=Sum('quantity'),cost=Sum('price') ).order_by('product__name',))

			else:
				items=list(IncomingItem.objects.filter(**filters).values('product__name','product__measurement_unit','brand__name','manf__name','invoice__provider__name','invoice__provider__identification','quantity','price','arrival_status','invoice__system_id','invoice__internal_reference','invoice__processedon','invoice__provider_reference').order_by('product__name',))



			reply['report_type']=report_type
			reply['output_option']=output_option
			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			reply['items']=items

			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			status=200


		

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	

class Distribution(APIView):
	'''
	Items arrive in pack. E.g. under INV90787,wemight have two laptops. We want to see where they are exactly now. We firstly locate the incoming invoice
	then we deal with the items CURRENT information only.

	Here accept as well RLCR, SYSTEM OR COMPANY ID of an item to get the system invoice and get the infos as necessary
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_distribution'])

		if have_right:

			
			
			search_invoice_by=request.query_params.get('option','system_id').strip()
			search_term=request.query_params.get('term','').strip()
			
			output_option=request.query_params.get('output','').strip().capitalize()
			invoice_filter={}
			invoice_id=0
			if search_invoice_by=='int_ref':
				invoice_filter['internal_reference']=search_term
			elif search_invoice_by=='system_id':
				invoice_filter['system_id']=search_term
			elif search_invoice_by=='item_rlrc_id':
				invoice_filter['incoming_item_invoice__institution_code']=search_term
			elif search_invoice_by=='item_manf_serial':
				invoice_filter['incoming_item_invoice__manf_serial']=search_term
			elif search_invoice_by=='item_tag':
				invoice_filter['incoming_item_invoice__tag']=search_term



			
			
			try:
				invoice_info=IncomingInvoice.objects.values('id','processedon','provider__name','internal_reference','system_id').get(**invoice_filter)
				#invoice found. So
				invoice_id=invoice_info['id']
				reply['invoice_info']=invoice_info
				status=200
			except:
				reply['detail']=_('ErrorInvoiceMissing')
				invoice_id=0
				stauts=400

			if invoice_id>0:
				#now get the items.
				item_info=list(IncomingItem.objects.filter(invoice_id=invoice_id).values('id','product__name','product__kind','brand__name','manf__name','price','arrival_status','current_status').order_by('product__name',))
				items_current_info=[];


				for i in item_info:
					item_detail=i#dictionary
					item_current_info={}
					item_current_info['kind']=item_detail['product__kind']
					item_current_info['arrival_status']=item_detail['arrival_status']
					item_current_info['pro_name']=item_detail['product__name']
					item_current_info['brand_name']=item_detail['brand__name']
					item_current_info['manf_name']=item_detail['manf__name']
					item_current_info['price']=item_detail['price']


					if item_detail['current_status']!='Lost':

						total_in_store=list(ItemInStore.objects.filter(item_id=item_detail['id']).values('store__name','current_status').annotate(total=Sum('quantity')))

						if len(total_in_store)>0:
							item_current_info['status']=total_in_store[0]['current_status']
							item_current_info['quantity']=total_in_store[0]['total']
							item_current_info['location']=_('InStore')
							item_current_info['location_name']=total_in_store[0]['store__name']
						else:
							#not in store. So check whom it is. Only for non-consumable
							if item_detail['product__kind']=='Non-consumable':
								try:

									state_info = OutgoingItem.objects.annotate(
										reciepent_name=Case(

										When(invoice__receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
										When(invoice__receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
										When(invoice__receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
										When(invoice__receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
										When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
										When(invoice__receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__give_to_id')).values('full_name'))),
										
										output_field=CharField())).values('given_status','given_quantity','invoice__receipent_type','invoice__processedon','reciepent_name').get(item_id=item_detail['id'],ownership_status=1)
									item_current_info['status']=state_info['given_status']
									item_current_info['quantity']=state_info['given_quantity']
									item_current_info['location']=state_info['invoice__receipent_type']
									item_current_info['location_name']=state_info['reciepent_name']
								except:
									item_current_info['status']=_('Undetermined')
									item_current_info['quantity']=_('Undetermined')
									item_current_info['location']=_('Undetermined')
									item_current_info['location_name']=_('Undetermined')
									
									
									


					else:
						item_current_info['status']='Lost'
						item_current_info['quantity']=-1
						item_current_info['location']="Lost"
						item_current_info['location_name']=""


					items_current_info.append(item_current_info)

				reply['items']=list(items_current_info)




			reply['output_option']=output_option
			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

		


		

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	

class Inventory(APIView):
	'''
	What item is in store and what is not in store
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_inventory'])

		if have_right:
	

			output_option=request.query_params.get('output','w').strip().lower()

			if output_option not in ['w','x']:
				output_option='w'

			products=request.query_params.get('products','') #csv
			kinds=request.query_params.get('kinds','').strip().capitalize()
			status=request.query_params.get('status','').strip()
			#not paged.
			filters={}
			if kinds in ['Consumable','Non-consumable']:
				filters['product__kind']=kinds

			products=csvFromUrlToNumbers(products)
			if products:
				filters['product_id__in']=products

			status=csvFromUrlToNumbers(status,num='str')

			if status:
				filters['current_status__in']=status


			item_info=list(IncomingItem.objects.filter(**filters).values('id','tag','institution_code','manf_serial','product__name','invoice__system_id','invoice__internal_reference','product__kind','brand__name','manf__name','price','arrival_status','current_status').order_by('product__name',))
			items_current_info=[];

			
			for item in item_info:
				item_detail=item#dictionary
				item_current_info={}
				item_current_info['kind']=item_detail['product__kind']
				item_current_info['arrival_status']=item_detail['arrival_status']
				item_current_info['pro_name']=item_detail['product__name']
				item_current_info['brand_name']=item_detail['brand__name']
				item_current_info['manf_name']=item_detail['manf__name']
				item_current_info['price']=item_detail['price']
				item_current_info['system_id']=item_detail['invoice__system_id']
				item_current_info['internal_reference']=item_detail['invoice__internal_reference']
				item_current_info['institution_code']=item_detail['institution_code']
				item_current_info['manf_serial']=item_detail['manf_serial']
				item_current_info['status']=item_detail['current_status']

				if item_detail['current_status']!='Lost':

					total_in_store=list(ItemInStore.objects.filter(item_id=item_detail['id']).values('store__name','current_status').annotate(total=Sum('quantity')))

					if len(total_in_store)>0:
						
						item_current_info['quantity']=total_in_store[0]['total']
						item_current_info['location']=_('InStore')
						item_current_info['location_name']=total_in_store[0]['store__name']
					else:
						#not in store. So check whom it is. Only for non-consumable

						

						if item_detail['product__kind']=='Non-consumable':
							try:

	
								state_info = OutgoingItem.objects.annotate(
									reciepent_name=Case(

									When(invoice__receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
									When(invoice__receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
									When(invoice__receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
									When(invoice__receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
									When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
									When(invoice__receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('invoice__give_to_id')).values('full_name'))),
									
									output_field=CharField())).values('given_status','given_quantity','invoice__receipent_type','invoice__processedon','reciepent_name').get(item_id=item_detail['id'],ownership_status=1)
								
								item_current_info['quantity']=state_info['given_quantity']
								item_current_info['location']=state_info['invoice__receipent_type']
								item_current_info['location_name']=state_info['reciepent_name']


							
							except:
								item_current_info['status']=_('Undetermined')
								item_current_info['quantity']=_('Undetermined')
								item_current_info['location']=_('Undetermined')
								item_current_info['location_name']=_('Undetermined')
	

				else:
					item_current_info['status']='Lost'
					item_current_info['quantity']=-1
					item_current_info['location']='Lost'
					item_current_info['location_name']=""


				items_current_info.append(item_current_info)

			reply['items']=list(items_current_info)


			reply['output_option']=output_option
			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			status=200

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class Depreciation(APIView):
	'''
	Depreciation report
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_depreciation'])

		if have_right:

			today=date.today()
			option=request.query_params.get('option','').lower().strip() #date month driven (needs below values), already depreciated or not yet depreciated
			products=request.query_params.get('products','') #csv
			depreciation_in_year=request.query_params.get('depreciation_in_year','') #
			depreciation_in_month=request.query_params.get('depreciation_in_month','') #
			if option not in ['dt','dep','notdep']:
				option='dt' #default items depreciate by year

			sql=""" SELECT initem.id AS id,initem.institution_code as institution_code,initem.manf_serial AS manf_serial,initem.current_status AS current_status, initem.arrivedon AS cameon,products.name,brands.name AS brandname
					,manf.name AS manfname,products.lasts_for_years AS lifespan,initem.price AS price,products.depreciation_method AS dep_method
					FROM logistic_incomingitem AS initem INNER JOIN inventory_product AS products ON products.id=initem.product_id
					INNER JOIN inventory_brand AS brands ON brands.id=initem.brand_id INNER JOIN inventory_manufacturer AS manf
					ON manf.id=initem.manf_id WHERE products.kind='Non-consumable'
				"""

			products=csvFromUrlToNumbers(products,reply_format='str')
			if products:
				sql=''.join([sql," AND products.id in ( ",products,")"])
				


			if option=='dt':

				try:
					depreciation_in_year=int(depreciation_in_year)
				except:
					depreciate_in_year=0

				try:
					depreciation_in_month=int(depreciation_in_month)
				except:
					depreciation_in_month=0

				allowed_years=range(2012,today.year + 50)
				months=range(1,13)

				if depreciation_in_year not in allowed_years:
					depreciation_in_year=today.year

				if depreciation_in_month not in months:
					depreciation_in_month=today.month

				sql=''.join([sql," AND Year(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))={0} AND MONTH(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))={1}"])
						
				sql=sql.format(depreciation_in_year,depreciation_in_month)

				reply['title']=_('RptDepreciationMonthYearBased')
				reply['month']=depreciation_in_month
				reply['year']=depreciation_in_year	
						
						

			elif option=='dep':
				#already depreciated products only. That means
				sql=''.join([sql," AND Year(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))<={0} AND MONTH(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))<={1}"])
						
				sql=sql.format(today.year,today.month)		

				reply['title']=_('RptDepreciationAlready')

			else:
				#anot yet depreciated
				sql=''.join([sql," AND Year(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))>={0} AND MONTH(DATE_ADD(initem.arrivedon, INTERVAL products.lasts_for_years YEAR))>={1}"])
						
				sql=sql.format(today.year,today.month)

				reply['title']=_('RptDeprecationNotYet')


			sql=''.join([sql," ORDER BY products.name"])	


			
			with connection.cursor() as cursor:
				cursor.execute(sql)
				rows=dictfetchall(cursor)
				item_info=list(rows)



			items_current_info=[];

			
			for i in item_info:

				item_detail=i#dictionary
				item_current_info={}
				
				
				item_current_info['pro_name']=item_detail['name']
				item_current_info['brand_name']=item_detail['brandname']
				item_current_info['manf_name']=item_detail['manfname']
				item_current_info['price']=item_detail['price']
				
				item_current_info['dep_method']=item_detail['dep_method']
				item_current_info['life_span']=item_detail['lifespan']
				item_current_info['institution_code']=item_detail['institution_code']
				item_current_info['manf_serial']=item_detail['manf_serial']
				
				item_current_info['acquired_on']=item_detail['cameon']
				item_current_info['status']=item_detail['current_status']




				if item_detail['current_status']!='Lost':

					total_in_store=list(ItemInStore.objects.filter(item_id=item_detail['id']).values('store__name','current_status').annotate(total=Sum('quantity')))

					if len(total_in_store)>0:
						
						item_current_info['quantity']=total_in_store[0]['total']
						item_current_info['location']=_('InStore')
						item_current_info['location_name']=total_in_store[0]['store__name']
					else:
						#not in store. So check whom it is. Only for non-consumable
						

						
						try:


							state_info = OutgoingItem.objects.annotate(
								reciepent_name=Case(

								When(invoice__receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('invoice__head_id')).values('name',))),
								When(invoice__receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__department_id')).values('full_name'))),
								When(invoice__receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__division_id')).values('full_name'))),
								When(invoice__receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('invoice__unit_id')).values('full_name'))),
								When(invoice__receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('invoice__office_id')).values('name'))),
								When(invoice__receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' '),'user__first_name')).filter(pk=OuterRef('invoice__give_to_id')).values('full_name'))),
								
								output_field=CharField())).values('given_status','given_quantity','invoice__receipent_type','invoice__processedon','reciepent_name').get(item_id=item_detail['id'],ownership_status=1)
							
							item_current_info['quantity']=state_info['given_quantity']
							item_current_info['location']=state_info['invoice__receipent_type']
							item_current_info['location_name']=state_info['reciepent_name']
						
						except:
							item_current_info['status']=_('Undetermined')
							item_current_info['quantity']=_('Undetermined')
							item_current_info['location']=_('Undetermined')
							item_current_info['location_name']=_('Undetermined')
	

				else:
					
					item_current_info['quantity']=-1
					item_current_info['location']='Lost'
					item_current_info['location_name']=""


				items_current_info.append(item_current_info)

			reply['items']=list(items_current_info)


			reply['option']=option
			reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			product_information=productInformation()
			reply['software_name']=product_information['product_name']

			reply['company_name']=product_information['company_name']

			status=200

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProductFlow(APIView):
	'''
	Fishcard report. Here, we take E.g. Laptop. We start at top. Arrived e.g. 90. Instore 5. Taken 7. Returned 2 etc.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,product_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['rpt_product_flow'])
		



		if have_right:
			try:
				reply['product']=Product.objects.values('id','name','category__name','measurement_unit','kind','min_value','max_value','depreciation_method','asset_code','lasts_for_years').get(pk=product_id)
				status=200
				output_option=request.query_params.get('output','').strip().lower()
				if output_option not in ['w','x']:
					output_option='w'

				sql=""" 

						SELECT "IN" as action, logistic_incominginvoice.processedon as processedon, 
						SUM(logistic_incomingitem.quantity) AS quantity

						FROM logistic_incomingitem 
						INNER JOIN logistic_incominginvoice ON (logistic_incomingitem.invoice_id = logistic_incominginvoice.id)
						WHERE (logistic_incomingitem.product_id = {0})
						GROUP BY logistic_incominginvoice.processedon

						UNION ALL



						SELECT "OT" as action, logistic_outgoinginvoice.processedon as processedon,
						-SUM(logistic_outgoingitem.given_quantity) AS quantity

						FROM logistic_outgoingitem 
						INNER JOIN logistic_outgoinginvoice ON (logistic_outgoingitem.invoice_id = logistic_outgoinginvoice.id)
						INNER JOIN logistic_incomingitem ON (logistic_incomingitem.id=logistic_outgoingitem.item_id)
						 WHERE (logistic_incomingitem.product_id = {1} AND logistic_outgoinginvoice.direction = "Direct")
						 GROUP BY logistic_outgoinginvoice.processedon HAVING SUM(logistic_outgoingitem.given_quantity)>0

						UNION ALL 

						
						

						 SELECT 'LT' as action,
						 logistic_itemunconventionalhistory.reportedon as processedon,
						 -COUNT(logistic_itemunconventionalhistory.id) as quantity
						
						 FROM logistic_itemunconventionalhistory
						 INNER JOIN logistic_incomingitem ON (logistic_incomingitem.id=logistic_itemunconventionalhistory.item_id)

						  WHERE (logistic_itemunconventionalhistory.factor = 'Lost' AND logistic_incomingitem.product_id = {2}

						   ) GROUP BY logistic_itemunconventionalhistory.reportedon HAVING COUNT(logistic_itemunconventionalhistory.id)>0 

						  UNION ALL

						 SELECT 'NLT' as action,
						 logistic_itemunconventionalhistory.reportedon as processedon,
						 COUNT(logistic_itemunconventionalhistory.id) as quantity
						
						 FROM logistic_itemunconventionalhistory
						 INNER JOIN logistic_incomingitem ON (logistic_incomingitem.id=logistic_itemunconventionalhistory.item_id)

						 WHERE (logistic_itemunconventionalhistory.factor = 'Found' AND logistic_incomingitem.product_id = {3} ) 
						 GROUP BY logistic_itemunconventionalhistory.reportedon HAVING COUNT(logistic_itemunconventionalhistory.id)>0 




						UNION ALL


						SELECT "RT" as action, logistic_returniteminvoice.processedon as processedon, 
						Count(logistic_returnitem.id) AS quantity
	                     

						FROM logistic_returnitem 
						INNER JOIN logistic_returniteminvoice ON (logistic_returnitem.invoice_id = logistic_returniteminvoice.id)
						 INNER JOIN logistic_outgoingitem ON (logistic_returnitem.item_id=logistic_outgoingitem.id)
						 INNER JOIN logistic_incomingitem ON (logistic_incomingitem.id=logistic_outgoingitem.item_id)

						  WHERE (logistic_incomingitem.product_id = {4})
						  GROUP BY logistic_returniteminvoice.processedon HAVING Count(logistic_returnitem.id)>0
												 		
						ORDER BY processedon asc, action ASC """.format(product_id,product_id,product_id,product_id,product_id)

				with connection.cursor() as cursor:
					cursor.execute(sql)
					rows=dictfetchall(cursor)
					reply['items']=list(rows)

				reply['output_option']=output_option
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				product_information=productInformation()
				reply['software_name']=product_information['product_name']

				reply['company_name']=product_information['company_name']



			except:
				reply['detail']=_('ErrorReportInvalidProduct')
				status=400

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class VisualizationPurchase(APIView):
	'''
	Purchase of items at a category and product level. Quantity and monetary data matters here.
	E.g. Laptop500,00rwf, 50

	@input: option (cat,pro,kind). how do we group it?
	

	Default group/output by categories
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['visualization_purchases'])

		if have_right:
			option=request.query_params.get('groupby','').lower().strip() #how do we want to group it?
			products=request.query_params.get('products','') #csv

			filters={}
			
			if products:
				filters['product_id__in']=products.split(',')
			
			
			stocked_on1=request.query_params.get('done_date1')
			stocked_on2=request.query_params.get('done_date2')
			stocked_portion_option=request.query_params.get('done_portion','y')
			stocked_option=request.query_params.get('done_date_option','e')
			stockedon_compare=dateQueryBuilder('invoice__processedon',stocked_portion_option,stocked_on1,stocked_on2,stocked_option)

			
			fields=[]

			if option=='kind':
				#purchases of this kind: Cons or Non-cons. Grop by kind
				fields.append('product__kind')

			else:
				#categories
				option='cat'


				fields.append('product__category__name')			


			if stockedon_compare:
				filters[stockedon_compare[0]]=stockedon_compare[1]
				#for month equal, we have additional data.
				if len(stockedon_compare)==4:
					filters[stockedon_compare[2]]=stockedon_compare[3]


			items=IncomingItem.objects.filter(**filters).values(*fields).annotate(total_cost=Sum(F('quantity') * F('price')), total_quantity=Sum('quantity')).order_by(*fields)
			reply['detail']=list(items)
			status=200
			reply['option']=option


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class VisualizationPurchaseTimeline(APIView):
	'''
	Purchase of items at a category and product level. Quantity and monetary data matters here.
	E.g. Laptop500,00rwf, 50

	@input: option (year,month). how do we group it?
	
	if by month, range of months cant be more than 24 months
	Default group/output by categories
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['visualization_purchases_timeseries'])

		if have_right:
			option=request.query_params.get('groupby','').lower().strip() #how do we want to group it? by month or year?
			products=request.query_params.get('products','') #cs
			start_year=request.query_params.get('start_year',0)
			end_year=request.query_params.get('end_year',0)
			start_month=request.query_params.get('start_month',0)
			end_month=request.query_params.get('end_month',0)
			fields_option=request.query_params.get('fields_option','').lower().strip() #cat =>category, pro=>products, kind=cons or non cons
			#note quantity have no effect on any except on pro



			filters={}

			today=date.today()
			allowed_years=list(range(appsettings.APPSET_RPT_V_TS_PURCHASE_STARTYEAR,today.year))
			
			if products:
				filters['product_id__in']=products.split(',')

			month_year_comparison=monthYearCompare(option,start_year,end_year,start_month,end_month,'invoice__processedon')

			filters[month_year_comparison[0]]=month_year_comparison[1]

			
			fields=[]

			annotates={}
			per_row_annotate={'total_cost':Sum(F('quantity') * F('price'))}

			if option=='month':
				#by year of purchase
				#fields.append('invoice__processedon__year')
				#fields.append('invoice__processedon__month')
				fields.append('period')
				annotates['period']=TruncMonth('invoice__processedon')

			else:
				#by year
				option='year'
				fields.append('period')	
				annotates['period']=TruncYear('invoice__processedon')


			if fields_option=='cat':
				fields.append('product__category__name')
			elif fields_option=='kind':
				fields.append('product__kind')
			elif fields_option=='pro':
				fields.append('product__name')
				per_row_annotate['total_quantity']=Sum('quantity')
			else:
				fields_option='cost'

			
			
			items=IncomingItem.objects.annotate(**annotates).filter(**filters).values(*fields).annotate(**per_row_annotate).order_by(*fields)
			
			reply['detail']=list(items)
			status=200
			reply['option']=option
			reply['fields_option']=fields_option


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

	






