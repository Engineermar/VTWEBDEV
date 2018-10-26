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

from dateutil import parser
from datetime import date,timedelta #for checking renewal date range.
import app.appsettings as appsettings
import math
from calendar import monthrange



def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]



def searchUserByNameQueryBuilder(search_value):
	'''
	Build a dynamic filter query to search a user by name. Note this is hard-coded to work with fields from model User

	@input search_value: a string that is expected to be name of a person.

	Based on number of spaces, we build the query here

	@output: a dictionary of filters that can be plugged into ORM filter
	'''

	#search employees by name
	filters={}
	if search_value:
		#split by space
		names=search_value.split(' ')
		length=len(names)
		if length==1:
			#no space. assume first name is only given
			filters['user__first_name__icontains']=names[0]
		elif length==2:
			#given two spaces
			filters['user__first_name__icontains']=names[0]
			filters['user__last_name__icontains']=names[1]
		elif length==3:
			#given 3 words. So assume the first two are first name, as it it common and hte last one is hte last name. E.g. Jean De Duee Hagarama : here Jean De Duee is all first name.
			first_name=' '.join([names[0],names[1]])
			last_name=names[2]
			filters['user__first_name__icontains']=first_name
			filters['user__last_name__icontains']=last_name
		elif length==4:
			first_name=' '.join([names[0],names[1],names[2]])
			last_name=names[3]
			filters['user__first_name__icontains']=first_name
			filters['user__last_name__icontains']=last_name

	return filters




def dateRangeBuilder(value,backdays,forworddays):
	'''

	Return an array with two date elements based on the given date

	@input: value is the base date, which is assumed to be in valid date format
	@input: backdays how many days to back from the given date (i.e.value)
	@input: forwarddays how many days to go forward from the given date.
	@output: array [date1,date2]

	So e.g. if value is 2018-09-15, go back 5 days and go forward 15 days. So we get items
	that dates 2018-09-10 and 2018-09-30

	It is assumed whoever calls ME is sure value is a valid date

	Return: List [Date1,Date2]
	'''

	backward=value - timedelta(days=backdays)
	forward=value + timedelta(days=forworddays)

	return [backward,forward]



def numericalQueryBuilder(field_name,value1,value2=None,option='e'):
	'''
	Build queries for numerical fields.

	@input: field_name the database field name on which the query will be build on (e.g. income)
	@value1: the first number
	@value2: the second number
	@option: how will the query be built. Options are:
		e=>equal
		gt=>greater than
		gte=>greater or equal
		lt=>less than
		lte=>less than or equal
		btn=>between value1 and value2. if value1 > value2, swap them

	@output: an array that can be put into filter of django ORM directly.

	so input can be 'salary',100,200,'btn'

	Here we are saying "Get records whose salary is between 100 and 200"

	Value1 and Value2 can be integers or decimals. Value2 can be skipped unless the comparison option is btn
	'''

	val1_ok=False
	val2_ok=True
	reply=[]





	try:
		value1=float(value1)
		val1_ok=True
	except:

		val1_ok=False

	if option=='btn':
		try:
			value2=float(value2)
			val2_ok=True
		except:
			val2_ok=False


	


	if val1_ok and val2_ok:
		if option=='e':
			#equal to
			
			reply.append(field_name)
			reply.append(value1)

		elif option=='gt':
			
			reply.append(field_name+'__gt')
			reply.append(value1)



		elif option=='gte':
			reply.append(field_name+'__gte')
			reply.append(value1)

		elif option=='lt':
			reply.append(field_name+'__lt')
			reply.append(value1)

		elif option=='lte':
			reply.append(field_name+'__lte')
			reply.append(value1)
		

		elif option=='btn':
			boundries=[]
			if value1>value2:
				boundries.append(value2)
				boundries.append(value1)
			elif value1<value2:
				boundries.append(value1)
				boundries.append(value2)

			if boundries:
				reply.append(field_name+'__in')
				reply.append(boundries)

	return reply





def dateQueryBuilder(field_name,portion,value1,value2=None,option='e'):
	'''
	Builds a complex query based on date.

	@input field_name : the database field name (e.g. birthdate)
	@input portion: which portion of the date do we care about. It can be:

		d=>date
		m=>month
		y=>year

	@input value1: first date in yyyy-mm-dd format
	@input value2: second date in yyyy-mm-dd format. It is optional unless option=='btn'
	@input option: how does the comparision work? It can be:

		e=>equal
		gt=>greater than
		gte=>greater or equal
		lt=>less than
		lte=>less than or equal
		btn=>between value1 and value2. if value1 > value2, swap them

	@output: an array that is ready to be plugged into django ORM filter
	'''

	val1_ok=False
	val2_ok=True
	reply=[]

	try:
		value1=parser.parse(str(value1)).date()
		val1_ok=True
	except:

		val1_ok=False

	

	if option=='btn':
		try:
			value2=parser.parse(str(value2)).date()
			val2_ok=True
		except:
			val2_ok=False


	


	if val1_ok and val2_ok:
		if portion=='d':

			if option=='e':
				#equal to
				
				reply.append(field_name)
				reply.append(value1)

			elif option=='gt':
				
				reply.append(field_name+'__gt')
				reply.append(value1)



			elif option=='gte':
				reply.append(field_name+'__gte')
				reply.append(value1)

			elif option=='lt':
				reply.append(field_name+'__lt')
				reply.append(value1)

			elif option=='lte':
				reply.append(field_name+'__lte')
				reply.append(value1)
			

			elif option=='btn':
				boundries=[]
				if value1>value2:
					boundries.append(value2)
					boundries.append(value1)
				elif value1<value2:
					boundries.append(value1)
					boundries.append(value2)

				if boundries:
					reply.append(field_name+'__range')
					reply.append(boundries)

		if portion=='m':

			

			dt1=date(value1.year,value1.month,1)
			
			if option=='e':
				#equal to
				
				reply.append(field_name+'__month')
				reply.append(value1.month)
				reply.append(field_name+'__year')
				reply.append(value1.year)

			elif option=='gt':

				reply.append(field_name+'__month__gt')
				reply.append(value1.month)
				reply.append(field_name+'__year')
				reply.append(value1.year)
	

			elif option=='gte':
				reply.append(field_name+'__month__gte')
				reply.append(value1.month)
				reply.append(field_name+'__year')
				reply.append(value1.year)

			elif option=='lt':
				reply.append(field_name+'__month__lt')
				reply.append(value1.month)
				reply.append(field_name+'__year')
				reply.append(value1.year)

			elif option=='lte':
				reply.append(field_name+'__month__lte')
				reply.append(value1.month)
				reply.append(field_name+'__year')
				reply.append(value1.year)
			

			elif option=='btn':
				dt2=date(value2.year,value2.month,1)
				boundries=[]
				if dt1>dt2:
					#date2 starts from 1, dt1 ends at last date of te month
					boundries.append(dt2)
					boundries.append(dt1)
				elif dt1<dt2:
					#date1 starts from 1, dt2 ends at last date of te month
					boundries.append(dt1)
					boundries.append(dt2)

				if boundries:
					reply.append(field_name+'__range')
					reply.append(boundries)

		if portion=='y':
		
			if option=='e':
				#equal to
				
				reply.append(field_name+'__year')
				reply.append(value1.year)


			elif option=='gt':

				reply.append(field_name+'__year__gt')
				reply.append(value1.year)
	

			elif option=='gte':
				reply.append(field_name+'__year__gte')
				reply.append(value1.year)

			elif option=='lt':
				reply.append(field_name+'__year__lt')
				reply.append(value1.year)


			elif option=='lte':
				reply.append(field_name+'__year__lte')
				reply.append(value1.year)

			

			elif option=='btn':
				
				boundries=[]
				if value1.year>value2.year:
					boundries.append(value2.year)
					boundries.append(value1.year)
				elif value1.year<value2.year:
					boundries.append(value1.year)
					boundries.append(value2.year)

				if boundries:
					reply.append(field_name+'__year__range')
					reply.append(boundries)
	return reply


def monthYearCompare(option,start_year,end_year,start_month,end_month,field_name):
	'''
	Creates a comparison option on month_year basis.
	option=>year/month
	E.g. a Timeseries report might be interested based on year from 2012 to 2017. Or month based, Jan 2014 to March 2015
	
	We don't check for option==year here cos it is needed in both year and months

	@input: option string month or nothing. if nothing, it will be year based
			start_year : the starting year
			end_year: the ending year
			start_month: the starting month
			end_month: the ending month
			field_name: the db field the comparison will be based/tied with
	@output: an array of ORM filter() pluggable data
	'''
	reply=[]
	today=date.today()
	allowed_years=list(range(appsettings.APPSET_RPT_V_TS_PURCHASE_STARTYEAR,today.year+1))
	allowed_months=list(range(1,13))
	
	try:
		start_year=int(start_year)
		end_year=int(end_year)

		if start_year in allowed_years and end_year in allowed_years:
			if end_year<=start_year:
				end_year=start_year + 1
		else:
			end_year=today.year
			start_year=end_year -2

	except:
		end_year=today.year
		start_year=end_year -2


	if end_year - start_year > appsettings.APPSET_RPT_V_TS_MAX_PERIOD:
		end_year=start_year + appsettings.APPSET_RPT_V_TS_MAX_PERIOD

		

	if option=='month':
		#timeseries based on month. Maximam is 24 months
		try:
			start_month=int(start_month)
			end_month=int(end_month)
			if start_month not in allowed_months or end_month not in allowed_months:
				end_month=today.month
				start_month=end_month -1
		except:
			end_month=today.month
			start_month=end_month -1

		date1=date(start_year,start_month,1)
		total_days_in_month=monthrange(end_year, end_month)
		
		date2=date(end_year,end_month,total_days_in_month[1])
		#are we in allowed range of months?
		gap_months=(date2.year - date1.year) * 12 + (date2.month - date1.month)

		

		if gap_months<0:
			#swap them
			dt=date1
			date1=date2
			date2=dt
			gap_months=-1 * gap_months

		if gap_months>appsettings.APPSET_RPT_V_TS_MAX_PERIOD:
			months_to_add=math.floor(appsettings.APPSET_RPT_V_TS_MAX_PERIOD * 365/12)
			date2=date1 + timedelta(days=months_to_add) #since it adds exact number of days, it might stop befor end of the month
			total_days_in_month=monthrange(date2.year,date2.month)
			date2=date(date2.year,date2.month,total_days_in_month[1])
	else:
		date1=date(start_year,1,1)
		date2=date(end_year,1,31)


	#return result

	reply.append(field_name+'__range')
	reply.append([date1,date2])

	return reply


def transferItemsQueryBuilding(e_kind,e_id):
	'''
	for items that were transefered from entity to entity, we want to build filters

	@input e_kind: entity kind (Employee, Head=>Office)
			e_id: entity id (id of the employee or hr entitty)

	@output: a dictionaryof filters


	Here, we are essentially limiting "itemst that were transfered FROM" without caring to whom they were transfered to
			
	'''
	filters={}

	

	
	filters['invoice__transfered_from_type']=e_kind
	if e_kind=='Head':
		filters['invoice__transfered_from_head_id']=e_id
	elif e_kind=='Department':
		filters['invoice__transfered_from_department_id']=e_id
	elif e_kind=='Division':
		filters['invoice__transfered_from_division_id']=e_id
	elif e_kind=='Unit':
		filters['invoice__transfered_from_unit_id']=e_id
	elif e_kind=='Employee':
		filters['invoice__transfered_from_id']=e_id		


	filters['invoice__direction']='Transfer'
	return filters


def distributionQueryBuilding(e_kind,e_id,item_filter,ownership_option):
	'''
	for distribution (ie.. items that were given), we want to build filters

	@input e_kind: entity kind (Employee, Head=>Office)
			e_id: entity id (id of the employee or hr entitty)
			ownership_option: what is the status of hte items we want? Choices include:
				inhand=>items the entty or employee currently has in his/her posession wheather they were directly taken from the store or transfered from another user
				inhand-direct=>items the entity or employee has with him/her but took the items directly from the store
				inhand-transfered=>items the entity or employee has with him/her but took the items were transfered to him/her from another employee
				lost=> items the employee has lost
			item_filter: list of item types to filter


	@output: a dictionary of filters that can be plugged into django ORM direclty
	'''
	filters={}

	ownership_status=0;
	got_items_thru='';


	if ownership_option=='inhand':
		#inhand items regardless of how they were obtained
		ownership_status=1

	elif ownership_option=='inhand-direct':
		#inhand but obtained from store directly
		ownership_status=1
		got_items_thru='Direct'

	elif ownership_option=='inhand-transfered':
		ownership_status=1
		got_items_thru='Transfer'

	elif ownership_option=='lost':
		ownership_status=3


	
	filters['invoice__receipent_type']=e_kind
	if e_kind=='Head':
		filters['invoice__head_id']=e_id
	elif e_kind=='Department':
		filters['invoice__department_id']=e_id
	elif e_kind=='Division':
		filters['invoice__division_id']=e_id
	elif e_kind=='Unit':
		filters['invoice__unit_id']=e_id
	elif e_kind=='Employee':
		filters['invoice__give_to_id']=e_id		

	if ownership_status>0:
		filters['ownership_status']=ownership_status

	if got_items_thru:
		filters['invoice__direction']=got_items_thru

	if item_filter:
		filters['item__product__kind']=item_filter


	return filters



def returnedItemsQueryBuilding(e_kind,e_id):
	'''
	for items that were returned by an entity

	@input e_kind: entity kind (Employee, Head=>Office)
			e_id: entity id (id of the employee or hr entitty)

	@output: a dictionaryof filters


	Here, we are essentially limiting "itemst that were returend by"
			
	'''
	filters={}

	
	filters['invoice__returner_type']=e_kind
	if e_kind=='Head':
		filters['invoice__head_id']=e_id
	elif e_kind=='Department':
		filters['invoice__department_id']=e_id
	elif e_kind=='Division':
		filters['invoice__division_id']=e_id
	elif e_kind=='Unit':
		filters['invoice__unit_id']=e_id
	elif e_kind=='Employee':
		filters['invoice__return_by_id']=e_id	

	return filters
