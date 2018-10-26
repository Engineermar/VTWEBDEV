from app.conf import base as settings
from tools.formtools import createErrorDataJSON,csvFromUrlToNumbers
from datetime import date
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse
from dateutil import parser

from django.db.models import Case, CharField, Count, F, OuterRef, Subquery, Sum, Value, When

from hr.models import Department, Division, Employee, Head, Office, Unit


from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo

from logistic.models import WareHouseTally,RequestInvoice,RequestedItem, IncomingInvoice,OutgoingInvoice,ReturnItemInvoice,ItemInStore,IncomingItem,Provider,OutgoingItem,ReturnItem,ProviderKind

from logistic.serializers import RequestInvoiceSerializer,ProcessRequestSerializer, ProviderKindSerializer,IncomingInvoiceSerializer,ProviderSerializer,OutgoingInvoiceSerializer,ReturnInvoiceSerializer,TransferInvoiceSerializer,HRStructureCheck
from inventory.models import Store

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import app.appsettings as appsettings



from tools.generators import generateProductTag,generateInvoiceCode,generateProcessingBatchCode

from tools.product import registerNewProductBrand,registerNewProductManafacturer,logisticProductInformation
import json
from tools.company import productInformation
from tools.history import addItemHistory
from tools.entities import entityInformation
from tools.build_quries import dateQueryBuilder
from tools.invoice_tools import invoiceIsEditable

from django.db.models.functions import Concat
from tools.publish import publishCatalogStructureJSON
from mailer.simplemail import emailNewRequestNotification
from tools.permissions import usersWithPermission



class SoftTransfer(APIView):
	'''
	This API is a temporary API that shouldnt be used anymore once migration of data is done
	for items that are in store, to move tem between entties. I.e. if an item is in Head A to softly transfer it to Employee B cos
	it is indeed with Employee B
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		user_id=request.user.id

		if userIsPermittedTo(user_id,['can_make_soft_transfer']):

			
			items=request.data.get('items') #this are currently in ItemInStore model
			give_to=request.data.get('give_to',0) #general receipent id. Its reference is based on receipent type below
			give_to_type=request.data.get('give_to_type','')

			err_msg={}

			hr_valid=HRStructureCheck(give_to_type,give_to,check_active=1)

			
			try:
				items=json.loads(items)
				if not items:
					err_msg['items']=_('ErrorInvalidItems')
			except:
				err_msg['items']=_('ErrorInvalidItems')

			if hr_valid:
				err_msg['give_to']=hr_valid

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:
				#all seems ok. Update both items current status and instore status
				OutgoingInvoice.objects.filter(outgoingitem_outgoinginvoice__id__in=items,outgoingitem_outgoinginvoice__ownership_status=1).update(head_id=None,department_id=None,office_id=None,unit_id=None,division_id=None,give_to_id=None)

				fields={'receipent_type':give_to_type}

				if give_to_type=='Employee':
					fields['give_to_id']=give_to
				elif give_to_type=='Head':
					fields['head_id']=give_to
				elif give_to_type=='Department':
					fields['department_id']=give_to
				elif give_to_type=='Division':
					fields['division_id']=give_to				
				elif give_to_type=='Unit':
					fields['unit_id']=give_to
				elif give_to_type=='Office':
					fields['office_id']=give_to									
				OutgoingInvoice.objects.filter(outgoingitem_outgoinginvoice__id__in=items,outgoingitem_outgoinginvoice__ownership_status=1).update(**fields)

			
				
				status=200
				reply['detail']=_('SoftTransferCompletedOk')

		else:
			
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class Inventory(APIView):
	'''
	Accompanies MoveOwnership API above to list inventory of items that are currently in possession of others
	or are instore.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['manage_inventory_items'])

		if have_right:
	

		

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


			inv_items=IncomingItem.objects.filter(**filters).values('id','tag','institution_code','manf_serial','product__name','invoice__system_id','invoice__internal_reference','product__kind','brand__name','manf__name','price','arrival_status','current_status').order_by('product__name',)
			
			try:
						
				page=request.query_params.get('page',1)
				paginator=Paginator(inv_items,appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS)
				data=paginator.page(page)
				status=200
			except PageNotAnInteger:
				data=paginator.page(1)
				status=200
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				item_info=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS
				reply['current_page']=page
			

				items_current_info=[];

				
				for item in item_info:
					item_detail=item#dictionary
					item_current_info={}
					item_current_info['id']=item_detail['id']
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
					item_current_info['instore']=2 #to be sure no soft transfer can appen
					item_current_info['og_id']=0

					if item_detail['current_status']!='Lost':

						total_in_store=list(ItemInStore.objects.filter(item_id=item_detail['id']).values('store__name','current_status').annotate(total=Sum('quantity')))

						if len(total_in_store)>0:
							
							item_current_info['quantity']=total_in_store[0]['total']
							item_current_info['location']=_('InStore')
							item_current_info['location_name']=total_in_store[0]['store__name']
							item_current_info['instore']=1
							item_current_info['og_id']=0
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
										
										output_field=CharField())).values('given_status','given_quantity','invoice__receipent_type','invoice__processedon','reciepent_name','id').get(item_id=item_detail['id'],ownership_status=1)
									
									item_current_info['quantity']=state_info['given_quantity']
									item_current_info['location']=state_info['invoice__receipent_type']
									item_current_info['location_name']=state_info['reciepent_name']
									item_current_info['og_id']=state_info['id']
									item_current_info['instore']=0


								
								except:
									item_current_info['status']=_('Undetermined')
									item_current_info['quantity']=_('Undetermined')
									item_current_info['location']=_('Undetermined')
									item_current_info['location_name']=_('Undetermined')
									item_current_info['instore']=2
									item_current_info['og_id']=0
		

					else:
						item_current_info['status']='Lost'
						item_current_info['quantity']=-1
						item_current_info['location']='Lost'
						item_current_info['location_name']=""
						item_current_info['instore']=2 #uknown
						item_current_info['og_id']=0


					items_current_info.append(item_current_info)

				reply['detail']=list(items_current_info)
			


			
		

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class DividePlace(APIView):
	'''
	Divide and place consumables. E.g. if there are 1000 Cartons of water in Store A, you can move the 400 to Store B

	Input: iteminstoreid, quantity and store to move to

	Note that if there are items with the same store and arrivedon date, we merge the quantities
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		user_id=request.user.id

		if userIsPermittedTo(user_id,["can_divide_place"]):
			dest_store=request.data.get('dest_store','')
			item_in_store_id=request.data.get('id','')
			new_quantity=request.data.get('quantity','')
			go_on=False #assume the item couldnt be located
			try:
				item=ItemInStore.objects.get(pk=item_in_store_id,item__product__kind='Consumable')
				existing_quantity=item.quantity
				go_on=True
			except:
				reply['detail']=_('ErrorItemNotFound')

			if go_on:
				err_msg={}
				try:
					new_quantity=float(new_quantity)
				except:
					new_quantity=0

				if new_quantity==0:
					err_msg['quantity']=_('ErrorDividePlaceZeroNotAllowed')
				elif new_quantity>existing_quantity:
					err_msg['quantity']=_('ErrorDividePlaceQuantityCantExceed') % {'max':existing_quantity}
				elif new_quantity==existing_quantity:
					err_msg['quantity']=_('ErrorDividePlaceSameQuantity')

				#check the new store?

				if not Store.objects.filter(pk=dest_store).exists():
					err_msg['dest_store']=_('ErrorDestinationStoreIsInvalid')


				if err_msg:
					reply['detail']=createErrorDataJSON(err_msg,2)
				else:
					#no error message so divide up

					#check now if we have same item with same arrival date
					try:
						instore=ItemInStore.objects.get(item_id=item.item_id,arrivedon=date.today(), store_id=dest_store)
						#we have the item so just update its quantity
						instore.quantity=float(instore.quantity) + new_quantity
						instore.save()
						reply['detail']=_('DividePlaceOk')
						reply['new_id']=instore.id
						status=200
					except:
						#we dont
					
						newly_placed_item=ItemInStore(item_id=item.item_id,quantity=new_quantity,arrivedon=date.today(), store_id=dest_store,current_status=item.current_status,processedby_id=user_id)
						newly_placed_item.save()
						if newly_placed_item:
							reply['new_id']=newly_placed_item.id
							reply['detail']=_('DividePlaceOk')
							#the source now
							remain_quantity=float(existing_quantity) - new_quantity
							reply['remain_quantity']=remain_quantity
							item.quantity=remain_quantity
							item.save()
							status=200
						else:
							reply['detail']=_('ErrorDividePlace')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)





class StoreToStore(APIView):
	'''
	Move all items in Store A to Store B. Here, we just care about the existence of store B.
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		user_id=request.user.id

		if userIsPermittedTo(user_id,['can_move_from_store_to_store']):

			dest_store=request.data.get('dest_store')
			src_store=request.data.get('src_store')
			
			err_msg={}

			if not Store.objects.filter(pk=dest_store).exists():
				err_msg['dest_store']=_('ErrorDestinationStoreIsInvalid')

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:
				#all seems ok. So select the items that are IN DIFFERENT store
				items=list(ItemInStore.objects.filter(store_id=src_store).values('id','store_id','arrivedon','current_status','quantity','item_id','item__product__kind'))
				update_ids=[]
				delete_ids=[]
				if items:
					for item in items:
						kind=item['item__product__kind']
						if kind=='Non-consumable':
							update_ids.append(item['id'])
						else:
							#it is consuamble so
							arrivedon=item['arrivedon']
							item_id=item['item_id']#incoming item
							qty=float(item['quantity'])
							current_status=item['current_status']
							delete_ids.append(item['id'])

							try:
								instore=ItemInStore.objects.get(item_id=item_id,arrivedon=arrivedon, store_id=dest_store)
								#we have the item so just update its quantity
								instore.quantity=float(instore.quantity) + qty
								instore.save()
								

							except:
								#we dont
							
								newly_placed_item=ItemInStore(item_id=item_id,quantity=qty,arrivedon=date.today(), store_id=dest_store,current_status=current_status,processedby_id=user_id)
								newly_placed_item.save()
				#do we have any updates to do?
				if update_ids:
					items=ItemInStore.objects.filter(pk__in=update_ids).exclude(store_id=dest_store).update(store_id=dest_store)
				if delete_ids:
					items=ItemInStore.objects.filter(pk__in=delete_ids).delete()
				status=200
				reply['detail']=_('StoreItemsMovedOK')

		else:
			
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class BatchUpdateItemStatus(APIView):
	'''
	update the current status of the items
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		user_id=request.user.id

		if userIsPermittedTo(user_id,['can_change_item_status']):

			
			items=request.data.get('items') #this are currently in ItemInStore model
			new_status=request.data.get('new_status','')
			err_msg={}

			
			try:
				items=json.loads(items)
				if not items:
					err_msg['items']=_('ErrorInvalidItems')
			except:
				err_msg['items']=_('ErrorInvalidItems')

			STATUS=[x[0] for x in settings.STATUS]
			if new_status not in STATUS:
				err_msg['new_status']=_('ErrorStatusChangeInvalidStatus')			


			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:
				#all seems ok. Update both items current status and instore status
				IncomingItem.objects.filter(pk__in=items,product__kind='Non-consumable').update(current_status=new_status)

				ItemInStore.objects.filter(item_id__in=items,item__product__kind='Non-consumable').update(current_status=new_status)
				
				status=200
				reply['detail']=_('StatusUpdatedOk')

		else:
			
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class MoveItemsInStore(APIView):
	'''
	Items in store A are checked to be moved to store B. Accept a store and list of items of that are currently in store.
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		user_id=request.user.id

		if userIsPermittedTo(user_id,['can_move_instore_items']):

			dest_store=request.data.get('dest_store')
			items=request.data.get('items') #this are currently in ItemInStore model
			err_msg={}

			if not Store.objects.filter(pk=dest_store).exists():
				err_msg['dest_store']=_('ErrorDestinationStoreIsInvalid')

			
			try:
				items=json.loads(items)
				if not items:
					err_msg['items']=_('ErrorMovingItemsInvalidItems')
			except:
				err_msg['items']=_('ErrorMovingItemsInvalidItems')


			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:
				#all seems ok. So select the items that are IN DIFFERENT store
				items=list(ItemInStore.objects.filter(pk__in=items).exclude(store_id=dest_store).values('id','store_id','arrivedon','current_status','quantity','item_id','item__product__kind'))
				update_ids=[]
				delete_ids=[]
				if items:
					for item in items:
						kind=item['item__product__kind']
						if kind=='Non-consumable':
							update_ids.append(item['id'])
						else:
							#it is consuamble so
							arrivedon=item['arrivedon']
							item_id=item['item_id']#incoming item
							qty=float(item['quantity'])
							current_status=item['current_status']
							delete_ids.append(item['id'])

							try:
								instore=ItemInStore.objects.get(item_id=item_id,arrivedon=arrivedon, store_id=dest_store)
								#we have the item so just update its quantity
								instore.quantity=float(instore.quantity) + qty
								instore.save()
								

							except:
								#we dont
							
								newly_placed_item=ItemInStore(item_id=item_id,quantity=qty,arrivedon=date.today(), store_id=dest_store,current_status=current_status,processedby_id=user_id)
								newly_placed_item.save()
				#do we have any updates to do?
				if update_ids:
					items=ItemInStore.objects.filter(pk__in=update_ids).exclude(store_id=dest_store).update(store_id=dest_store)
				if delete_ids:
					items=ItemInStore.objects.filter(pk__in=delete_ids).delete()
				status=200
				reply['detail']=_('ItemsMovedToNewStoreSuccessfully')

		else:
			
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ItemsInStore(APIView):
	'''
	Items that are currently instore for management purposes.
	'''

	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=200

		user_id=request.user.id

		if userIsPermittedTo(user_id,['manage_instore_items']):

			products=request.query_params.get('products','') #csv
			stores=request.query_params.get('stores','') #csv
			kinds=request.query_params.get('kinds','').strip().capitalize()
			item_status=request.query_params.get('status','').strip()			

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
			
		
			items=ItemInStore.objects.filter(**filters).values('id','quantity','item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price','item__expire_on','item__tag','current_status','store__name','item__institution_code','item__manf_serial','store_id','item__product__kind','item_id' ).order_by('item__product__name',)

			try:
						
				page=request.query_params.get('page',1)
				paginator=Paginator(items,appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS)
				data=paginator.page(page)
			except PageNotAnInteger:
				data=paginator.page(1)
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				reply['detail']=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS
				reply['current_page']=page


		else:
			status=400
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class ReverseOutgoing(APIView):
	'''
	One items are given, they can be reversed. This one is not an edit.


	=>an entire invoice can be cancelled
	=>individual items can be cancelled
	=>Cancellation not allowed if an item is reported as returned or transfered

	affects warehousetally as necessary
	itemsinstore

	if the invoice is empty, set the request invoice to unprocessed

	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400
		user_id=request.user.id
		have_right=userIsPermittedTo(user_id,['reverse_outgoing'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			given_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific given item instead of the whole thing
			try:
				given_item_id=int(given_item_id)
			except:
				given_item_id=0

			go_on=False #assume the parent give invoice was not found or is old and we cant continue


			try:
				give_invoice=OutgoingInvoice.objects.get(pk=invoice_id,direction="Direct")
				#can it be edited now?
				if invoiceIsEditable(give_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('GivenReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorGivenNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id}
				if given_item_id>0:
					#specific item
					filters['pk']=given_item_id


				#so who returend it?
					

				given_items=list(OutgoingItem.objects.filter(**filters).values('item_id','id','transfered_item_id','given_from_store_id','given_status','given_quantity','item__product__kind','arrived_to_store','ownership_status')) #contains list now
				
				#now select the items that were GIVEN in the first place
				if given_items:
					
				
					data=[]#each given items information
					given_item_ids=[]#primary column. used for checking returns only
					tally_dates={}#for warehouse history management
					for r_item in given_items:

						if r_item['ownership_status']==5:
							reply['detail']=_('ErrorReverseGivenItemsAlreadyTransfered')
							go_on=False
							break

						if r_item['ownership_status']==2:
							reply['detail']=_('ErrorReverseGivenItemsAlreadyReturned')
							go_on=False
							break


						given_item_ids.append(r_item['id'])

						dt=r_item['arrived_to_store']

						tally_date='-'.join([str(dt.year),str(dt.month),'1'])

						tally_date=parser.parse(str(tally_date)).date()

						if tally_dates.get(tally_date,'')=='':
							tally_dates[tally_date]=[]

						#add the item and its quantity now
						tally_dates[tally_date].append({'given_status':r_item['given_status'],'kind':r_item['item__product__kind'],'item_id':r_item['item_id'],'store_id':r_item['given_from_store_id'],'given_quantity':r_item['given_quantity']})

						
						
						data.append({
							'item_id':r_item['item_id'],
							'given_from_store_id':r_item['given_from_store_id'],
							'given_status':r_item['given_status'],
							'given_quantity':r_item['given_quantity'],
							'kind':r_item['item__product__kind'],
							'arrived_to_storeon':r_item['arrived_to_store']
							})


					

					if go_on:
						#no item is known to have been transfered or returned.
						#if not currently in store, put it back in store as well
						#put to store:
						put_to_store=[]

						
						for info in data:
							#info is now a dictionary. Check if item is in store or not?
							kind=info['kind'] #consumable or not?
							
							if kind=='Non-consumable':
								

								if not ItemInStore.objects.filter(item_id=info['item_id']).exists():
									#add to item
									save_new_to_store=ItemInStore(item_id=info['item_id'],store_id=info['given_from_store_id'],quantity=1,processedby_id=user_id,current_status=info['given_status'],arrivedon=info['arrived_to_storeon'])
									put_to_store.append(save_new_to_store)
									
							else:
								#this is a Consumable item. Hence, we care about its quantity. So we will check for exists first
								try:

									itemsin_store=ItemInStore.objects.get(item_id=info['item_id'],store_id=info['given_from_store_id'],arrivedon=info['arrived_to_storeon'])
									itemsin_store.quantity=float(itemsin_store.quantity) + float(info['given_quantity'])
									
									
									itemsin_store.save()

								except:
									save_new_to_store=ItemInStore(item_id=info['item_id'],store_id=info['given_from_store_id'],quantity=info['given_quantity'],processedby_id=user_id,current_status=info['given_status'],arrivedon=['arrived_to_storeon'])
									put_to_store.append(save_new_to_store)
							


						if put_to_store:
							#put items to the store
							
							ItemInStore.objects.bulk_create(put_to_store)

						#update warehousetally report
						if tally_dates:
							new_tallies=[]
							for dt in tally_dates:
								arrivedon_mon=dt.month
								arrivedon_year=dt.year
								arrivedon='-'.join([str(arrivedon_year),str(arrivedon_mon),'01'])
								items_list=tally_dates[dt]#a dictionary in form of item_id,store_id,given_quantity
								for item_info in items_list:
									#a dictionary now
									#({'item_id':r_item['item_id'],'store_id':r_item['given_from_store_id'],'given_quantity':r_item['given_quantity']})
									item_id=item_info['item_id']
									store_id=item_info['store_id']#it was given from tis store
									given_quantity=item_info['given_quantity']#this much was given
									kind=item_info['kind']#consuamble or non-consumable
									status=item_info['given_status']
									#check if the item was tallied
									if kind=='Non-consumable':
										#non consumable
										if not WareHouseTally.objects.filter(item_id=item_id,for_month=arrivedon).exists():
											#add it to tally now
											new_tally=WareHouseTally(item_id=item_id,store_id=store_id,for_month=arrivedon,quantity=1,current_status=status)
											new_tallies.append(new_tally)
									else:
										#it is a consumable product.
										try:

											tally_info=WareHouseTally.objects.get(item_id=item_id,store_id=store_id,for_month=arrivedon)
											tally_info.quantity=float(tally_info.quantity) + float(given_quantity)
											tally_info.save()
										except:
											new_tally=WareHouseTally(item_id=item_id,store_id=store_id,for_month=arrivedon,quantity=given_quantity,current_status=status)
											new_tallies.append(new_tally)

							if new_tallies:
								
								WareHouseTally.objects.bulk_create(new_tallies)

						#delete the items now
						stocked_out=OutgoingItem.objects.filter(pk__in=given_item_ids)
						stocked_out.delete()



						status=200

						if given_item_id==0:
							#delete the whole invoice
							give_invoice.delete()
							reply['detail']=_('StockOutReverseOk')
						else:
							reply['detail']=_('StockOutReverseItemOk')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class UpdateStockedOutItemQuantity(APIView):
	'''
	Works only for Consumables. For e.g. if water is given 20cartons but later discovered it is 10cartons, we can edit that quantity

	If the quantity is higher, put it back to te store. Adjust tally based on date

	if less, reduce store quantity based on date. IE.g. if it is not in current month, just attach tally. If now, reduce the quantity of te item in te store


	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400
		user_id=request.user.id
		have_right=userIsPermittedTo(user_id,['can_edit_stocked_quantity'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			given_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific given item instead of the whole thing
			new_quantity=request.data.get('quantity',0)
			try:
				given_item_id=int(given_item_id)
			except:
				given_item_id=0

			try:
				new_quantity=float(new_quantity)
			except:
				new_quantity=0

			go_on=False #assume the parent give invoice was not found or is old and we cant continue

			err_msg={}

			if given_item_id<=0:
				err_msg['rid']=_('ErrorStockedOutItemNotFound')

			if new_quantity<=0:
				err_msg['quantity']=_('ErrorStockedOutItemEditQuantityError')

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:

				#is the invoice correct now?
				try:
					give_invoice=OutgoingInvoice.objects.get(pk=invoice_id,direction="Direct")
					#can it be edited now?
					if invoiceIsEditable(give_invoice.processedon):
						go_on=True
					else:
						reply['detail']=_('GivenReverseInvalidTooOld')

				except:
					reply['detail']=_('ErrorGivenNotFound')


			#should we continue?
			if go_on and given_item_id>0:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id,'pk':given_item_id,'item__product__kind':'Consumable'}


				process_item=False

				try:
					og_item=OutgoingItem.objects.get(**filters)
					given_quantity=float(og_item.given_quantity) #what was given originally

					difference=new_quantity - given_quantity
					if difference!=0:
						process_item=True
					else:
						reply['detail']=_('ErrorStockedOutItemQuantityEditUnchanged')

				except:
					reply['detail']=_('ErrorStockedOutItemNotFound')

				#should we attempt to process the change now?

				if process_item:
					try:

						itemsin_store=ItemInStore.objects.get(item_id=og_item.item_id,store_id=og_item.given_from_store_id,arrivedon=og_item.arrived_to_store)
						#the same kind of store does exist inthe store still. So act on it now
						if difference<=0:
							#increase existing quantity now
							updated_quantity=float(itemsin_store.quantity) + (-1 * difference)
						else:
							#decrease instore quantity now
							updated_quantity=float(itemsin_store.quantity) - difference
							if updated_quantity<=0:
								updated_quantity=0
						itemsin_store.quantity=updated_quantity
						itemsin_store.save()
					except:
						if difference>0:
							save_new_to_store=ItemInStore(item_id=og_item.item_id,store_id=og_item.given_from_store_id,quantity=difference,processedby_id=user_id,current_status=og_item.given_status,arrivedon=og_item.arrived_to_store)
							save_new_to_store.save()

					og_item.given_quantity=new_quantity
					og_item.save()

					tally_date='-'.join([str(og_item.arrived_to_store.year),str(og_item.arrived_to_store.month),'01'])
					#check if we have the item tallied for the give nmonth/year
					try:
						tally_item=WareHouseTally.objects.get(item_id=og_item.item_id,store_id=og_item.given_from_store_id,for_month=tally_date)
						#we have it. So change its quantity now
						if updated_quantity<=0:
							tally_item.delete()
						else:
							tally_item.quantity=updated_quantity
							tally_item.save()	
					except:
						#we didnt find it in the store. If processed in the past, add it
						today=date(date.today().year,date.today().month,1)
						tally_date=parser.parse(str(tally_date)).date()
						if today>tally_date:
							new_tally=WareHouseTally(item_id=og_item.item_id,store_id=og_item.given_from_store_id,for_month=tally_date,quantity=new_quantity)
							new_tally.save()

					status=200
					reply['detail']=_('StockedOutItemQanityChanged')

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ReverseReturn(APIView):
	'''
	One items are returned, they can be reversed. Since we cant edit items, reverse is an option we have. Reversing depends on age
	of the return

	=>an entire return can be cancelled
	=>individual items of a return can be cancelled

	affects warehousetally as necessary
	itemsinstore

	Return the item to the entity that took it. But if any of the items is already known to be with another entity, reject te operation
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_returniteminvoice'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			returned_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific returned item instead of the whole thing
			try:
				returned_item_id=int(returned_item_id)
			except:
				returned_item_id=0

			go_on=False #assume the parent return invoice was not found or is old and we cant continue


			try:
				return_invoice=ReturnItemInvoice.objects.get(pk=invoice_id)
				#can it be edited now?
				if invoiceIsEditable(return_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('ReturnReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorReturnNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id}
				if returned_item_id>0:
					#specific item
					filters['pk']=returned_item_id


				#so who returend it?
					

				returned_items=list(ReturnItem.objects.filter(**filters).values('item_id','item__item_id','id')) #contains list now
					
				#now select the items that were GIVEN in the first place
				if returned_items:
					stockout_pks=[]
					incoming_item_ids=[] #used to remove from store
					returned_item_ids=[]
					for r_item in returned_items:
						#r_item is dictionay of item_id,item__item_id keys
						
						stockout_pks.append(r_item['item_id'])
						incoming_item_ids.append(r_item['item__item_id'])
						returned_item_ids.append(r_item['id'])

					#is any of the item currently in possesion with any one?



					if OutgoingItem.objects.filter(item_id__in=incoming_item_ids,ownership_status=1).exists():
						#some items are currently in possession by someone else
						reply['detail']=_('ErrorReverseReturnItemsAlreadyGiven')

					else:
						#no item is known to be given to any other entity. So rest the ownership status

						
						#if currently in store, delete it from store. Put warehousetally in order tho

						tally_dates={}

						instore_items=ItemInStore.objects.filter(item_id__in=incoming_item_ids)

						for instore_item in instore_items:
							pk_id=instore_item.id
							incoming_item_id=instore_item.item_id
							
							arrivedon_mon=instore_item.arrivedon.month
							arrivedon_year=instore_item.arrivedon.year
							arrivedon='-'.join([str(arrivedon_year),str(arrivedon_mon),'01'])

							if tally_dates.get(arrivedon,'')=='':
								tally_dates[arrivedon]=[]
							tally_dates[arrivedon].append(instore_item.item_id)

						#do we have tally items now
						if tally_dates:
							#yes.
							for tdate in tally_dates:
								item_ids=tally_dates[tdate]
								ware_house=WareHouseTally.objects.filter(for_month=tdate,item_id__in=item_ids)
								#delete the item now
								ware_house.delete()


						#now delete from te store
						instore_items.delete()
						stocked_out=OutgoingItem.objects.filter(pk__in=stockout_pks).update(ownership_status=1)

						
						#delete the returned items first
						r_items=ReturnItem.objects.filter(pk__in=returned_item_ids)
						r_items.delete()

						status=200

						if returned_item_id==0:
							#delete the whole invoice
							return_invoice.delete()
							reply['detail']=_('ReturnReverseOk')
						else:
							reply['detail']=_('ReturnReverseItemOk')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	






class UpdateStatusReturnedItem(APIView):
	'''
	An item which was returend requires a status when it was returned. Here, we can change that. We don't have to care about
	where it is and stuff here. Just make the status change and continue
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_edit_returend_items_status'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			returned_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific returned item instead of the whole thing

			go_on=False #assume the invoice couldt nbe found or is old
			try:
				return_invoice=ReturnItemInvoice.objects.get(pk=invoice_id)
				#can it be edited now?
				if invoiceIsEditable(return_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('ReturnReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorReturnNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id,'pk':returned_item_id}
				#get the item now
				try:
					returned_item=ReturnItem.objects.get(**filters)
					STATUS=[x[0] for x in settings.STATUS]
					new_status=request.data.get('status','').strip().capitalize()
					if new_status not in STATUS:
						reply['new_status']=_('ErrorInvalidStatus')
					else:
						returned_item.return_status=new_status
						returned_item.save()
						status=200
						reply['detail']=_('ReturnedItemStatusUpdated')

				except:
					reply['detail']=_('ErrorReturnedItemNotFound')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	

class UpdateStatusTransferItem(APIView):
	'''
	An item which was transfered requires a status when it was transfered. Here, we can change that.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_edit_transfered_items_status'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			transfered_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific returned item instead of the whole thing

			go_on=False #assume the invoice couldt nbe found or is old
			try:
				transfer_invoice=OutgoingInvoice.objects.get(pk=invoice_id,direction="Transfer")
				#can it be edited now?
				if invoiceIsEditable(transfer_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('TransferReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorTransferNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id,'pk':transfered_item_id}
				#get the item now
				try:
					transfered_item=OutgoingItem.objects.get(**filters)
					STATUS=[x[0] for x in settings.STATUS]
					new_status=request.data.get('status','').strip().capitalize()
					if new_status not in STATUS:
						reply['new_status']=_('ErrorInvalidStatus')
					else:
						transfered_item.given_status=new_status
						transfered_item.save()
						status=200
						reply['detail']=_('TransferedItemStatusUpdated')

				except:
					reply['detail']=_('ErrorTransferedItemNotFound')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class UpdateStatusStockedOutItem(APIView):
	'''
	An item which was stockedout requires a status when it was given. Here, we can change that.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_edit_stocked_out_items_status'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			stockout_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific returned item instead of the whole thing

			go_on=False #assume the invoice couldt nbe found or is old
			try:
				stockout_invoice=OutgoingInvoice.objects.get(pk=invoice_id,direction="Direct")
				#can it be edited now?
				if invoiceIsEditable(stockout_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('GivenReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorGivenNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id,'pk':stockout_item_id}
				#get the item now
				try:
					stockout_item=OutgoingItem.objects.get(**filters)
					STATUS=[x[0] for x in settings.STATUS]
					new_status=request.data.get('status','').strip().capitalize()
					if new_status not in STATUS:
						reply['new_status']=_('ErrorInvalidStatus')
					else:
						stockout_item.given_status=new_status
						stockout_item.save()
						status=200
						reply['detail']=_('StockOutItemStatusUpdated')

				except:
					reply['detail']=_('ErrorStockedOutItemNotFound')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ReverseTransfer(APIView):
	'''
	Once items are transfered, they can be reversed. This can be ALL items (thus deleting the transfer entirely)
	or specific items only

	This doesnt affect itemsinstore or warehouse tally
	
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['reverse_transfer'])

		if have_right:
			invoice_id=request.data.get('id') #the invoice id. needed in both deletion scenarios
			transfered_item_id=request.data.get('rid',0) #if given, it means we need to delete a specific transfered item instead of the whole thing
			try:
				transfered_item_id=int(transfered_item_id)
			except:
				transfered_item_id=0

			go_on=False #assume the parent transfer invoice was not found or is old and we cant continue


			try:
				transfer_invoice=OutgoingInvoice.objects.get(pk=invoice_id,direction='Transfer')
				#can it be edited now?
				if invoiceIsEditable(transfer_invoice.processedon):
					go_on=True
				else:
					reply['detail']=_('TransferReverseInvalidTooOld')

			except:
				reply['detail']=_('ErrorTransferNotFound')


			#should we continue?
			if go_on:
				#yes continue. but do we undo all all items or specific item?
				filters={'invoice_id':invoice_id}
				if transfered_item_id>0:
					#specific item
					filters['pk']=transfered_item_id


				transfered_items=list(OutgoingItem.objects.filter(**filters).values('id','transfered_item_id')) #contains list now
				
				#now select the items that were GIVEN in the first place
				if transfered_items:
					
					trans_auto_ids=[] #used to remove from store
					transfered_item_ids=[]
					for r_item in transfered_items:
						#r_item is dictionay of item_id,item__item_id keys
						trans_auto_ids.append(r_item['id']) #autonumber of the actual items that are part of the transfer invoice
						transfered_item_ids.append(r_item['transfered_item_id']) #the items that were transfered in the first place (i.e. part of the Outgoing Operation)

					
					
					given_items_filter={'id__in':transfered_item_ids,'ownership_status':5}
				

					OutgoingItem.objects.filter(**given_items_filter).update(ownership_status=1)


					
					#delete the returned items first
					r_items=OutgoingItem.objects.filter(pk__in=trans_auto_ids)
					r_items.delete()

					status=200

					if transfered_item_id==0:
						#delete the whole invoice
						transfer_invoice.delete()
						reply['detail']=_('TransferReverseOk')
					else:
						reply['detail']=_('TransferReverseItemOk')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProviderKindAdd(APIView):
	'''
	Add kind of possible suppliers/providers of items
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_providerkind'])

		if have_right:
			data=request.data
			serializer=ProviderKindSerializer(data=data)
			if serializer.is_valid():
				#add the provider
				content=serializer.validated_data
				

				providerkind=ProviderKind(name=content['name'],processedby_id=request.user.id )
				providerkind.save()
				if providerkind:
					reply['detail']=_('SupplierKindAddOk')
					reply['new_id']=providerkind.id
					status=200
					publishCatalogStructureJSON()
				else:
					reply['detail']=_('ErrorSupplierKindAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProviderKindEdit(APIView):
	'''
	Edit kind of possible suppliers/providers of items
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,kind_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_providerkind'])

		if have_right:
			#does the kind exist:
			try:
				providerkind=ProviderKind.objects.get(pk=kind_id)
				#exists well. So check it now now
				data=request.data
				serializer=ProviderKindSerializer(data=data,current_id=kind_id)
				if serializer.is_valid():
					#add the provider
					content=serializer.validated_data
					providerkind.name=content['name']
					providerkind.save()
					publishCatalogStructureJSON()
					reply['detail']=_('SupplierKindUpdateOk')

					status=200
					
				else:
					reply['detail']=createErrorDataJSON(serializer.errors)

			except:
				reply['detail']=_('ErrorLogisticInvalidSupplierKind')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ProviderKindDelete(APIView):
	'''
	Delete supplier kind
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,kind_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_providerkind'])

		if have_right:
			#does the kind exist:
			try:
				providerkind=ProviderKind.objects.get(pk=kind_id)
				#exists well. But do we have shops under it?
				if Provider.objects.filter(kind_id=kind_id).exists():
					reply['detail']=_('ErrorLogisiticDeleteSupplierKindSuppliersExist')
				else:
					providerkind.delete()
					status=200
					reply['detail']=_('SupplierKindDeleteOk')
					publishCatalogStructureJSON()
				
			except:
				reply['detail']=_('ErrorLogisticInvalidSupplierKind')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProviderKinds(APIView):
	'''
	Simply supply the kinds of suppliers we have registered so far.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,format=None):
		reply={}
		status=200

		have_right=userIsPermittedTo(request.user.id,['add_providerkind','change_providerkind','delete_providerkind'])

		reply['edit']=have_right
		reply['detail']=list(ProviderKind.objects.all().values('id','name').order_by('name'))

		return JsonResponse(reply,status=status)




class ProviderSearch(APIView):
	'''
	Locate a given provider. Open to except employees
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_suppliers'])
		


		if have_right:
			filters={}
			name=request.query_params.get('name','').strip()
			kind=request.query_params.get('kind','').strip()
			option=request.query_params.get('option','brief').strip().lower()
			try:
				kind=int(kind)
			except:
				kind=0
			if len(name)>0:
				filters['name__icontains']=name

			if kind>0:
				filters['kind_id']=kind

			if option not in ['brief','complete']:
				option='brief'

			if option=='brief':
				reply['detail']=list(Provider.objects.filter(**filters).values('id','name').order_by('name',))
			else:
				reply['detail']=list(Provider.objects.filter(**filters).values('id','name','kind__name','kind_id','phone','identification','email').order_by('name',))

			status=200

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ProviderAdd(APIView):
	'''
	Providers are shops, NGOs etc which provide items to MoJ. We had them here. Only logistic officer can do it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_provider'])

		if have_right:
			data=request.data
			serializer=ProviderSerializer(data=data)
			if serializer.is_valid():
				#add the provider
				content=serializer.validated_data
				

				provider=Provider(name=content['name'],identification=content['identification'],address=content['address'], email=content['email'] ,  phone=content['phone'],www=content['www'],kind_id=content['kind'],processedby_id=request.user.id )
				provider.save()
				if provider:
					reply['detail']=_('SupplierAddOk')
					reply['id']=provider.id
					status=200
				else:
					reply['detail']=_('ErrorSupplierAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ProviderEdit(APIView):
	'''
	Edit providers
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_provider'])

		if have_right:
			try:
				reply['detail']=Provider.objects.values('id','name','identification','address','email','phone','www','kind_id').get(pk=id)
				status=200
			except:
				reply['detail']=_('ErrorLogisticSupplierMissing')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

	def post(self,request,id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_provider'])

		if have_right:
			try:
				provider=Provider.objects.get(pk=id)
				data=request.data
				serializer=ProviderSerializer(data=data,current_id=id)
				if serializer.is_valid():
					#add the provider
					content=serializer.validated_data
					

					provider.name=content['name']
					provider.identification=content['identification']
					provider.address=content['address']
					provider.email=content['email']
					provider.phone=content['phone']
					provider.www=content['www']
					provider.kind_id=content['kind']
					provider.save()
					status=200
					reply['id']=id
					reply['detail']=_('SupplierUpdateOk')
				else:
					reply['detail']=createErrorDataJSON(serializer.errors)

			except:
				reply['detail']=_('ErrorLogisticSupplierMissing')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProviderDelete(APIView):
	'''
	Delete a provider here
	'''
	permission_classes = [TokenHasReadWriteScope]
	

	def post(self,request,id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_provider'])

		if have_right:
			try:
				provider=Provider.objects.get(pk=id)
				if IncomingInvoice.objects.filter(provider_id=id).exists():
					reply['detail']=_('ErrorSupplierDeleteInvoiceExists')
				else:
					status=200
					provider.delete()
					reply['detail']=_('SupplierDeleteOk')

			except:
				reply['detail']=_('ErrorLogisticSupplierMissing')



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class Tags(APIView):
	'''
	Get tags of items
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_print_tags'])

		if have_right:
			try:
				reply['invoice_info']=IncomingInvoice.objects.values('system_id','processedon','provider__name','provider__identification').get(pk=invoice_id)
				items=list(IncomingItem.objects.filter(invoice_id=invoice_id).exclude(tag=None).values('tag','manf_serial','institution_code','product__name','brand__name','manf__name','product__asset_code'))
				status=200
				reply['detail']=list(items)

				product_information=productInformation()
				
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
			except:
				reply['detail']=_('ErrorInvoiceMissing')

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class NewIncoming(APIView):
	'''
	Newly arrived items are processed here. The process can be complicated if multiple items are being processed. For non-consumables, we generate unique IDs as well
	if invoice_id=0, it means the invoice should be added now. Else, append the items to the invoice only.
	Note items come one by one here.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,invoice_id,format=None):
		reply={}
		status=400

		user_id=request.user.id

		have_right=userIsPermittedTo(user_id,['add_incominginvoice'])

		if have_right:
			data=request.data
			append_to_invoice=0
			try:

				invoice_id=int(invoice_id)
			except:
				invoice_id=0

			boolean_process_invoice=False

			if invoice_id==0:
				#add invoice. Do serializer here.
				
				serializer=IncomingInvoiceSerializer(data=data,current_id=invoice_id)
				boolean_process_invoice=True


			else:
				#does the invoice exist? If so, may be there is a need to change things.
				#Perhaps there is a better way to do this since this could be costly. The solution, would be batch processing but alas
				#Client demanded it not be batch processing and this is the hack avaliable for now
				try:
					incoming_invoice=IncomingInvoice.objects.get(pk=invoice_id)
				
					serializer=IncomingInvoiceSerializer(data=data,current_id=invoice_id)
					boolean_process_invoice=True

				except:
					reply['detail']=_('ErrorIncomingItemsInvalidInvoice')
					boolean_process_invoice=False


			if boolean_process_invoice:


				if serializer.is_valid():
					content=serializer.validated_data

					if invoice_id==0:
						system_id=generateInvoiceCode()

						invoice=IncomingInvoice(system_id=system_id,provider_id=content['provider'],processedon=content['processedon'],processedby_id=request.user.id,  provider_reference=content['provider_reference'],internal_reference=content['internal_reference'] )
						invoice.save()
						if invoice:
							append_to_invoice=invoice.id
							#item_generateProcessingBatchCode=generateProcessingBatchCode(invoice.id, 'NV')
						else:

							reply['detail']=_('ErrorIncomingInvoiceAddError')



					else:
						#update the information but only if it is valid age
						if invoiceIsEditable(incoming_invoice.processedon):
			
							incoming_invoice.provider_id=content['provider']
							incoming_invoice.processedon=content['processedon']
							incoming_invoice.provider_reference=content['provider_reference']
							incoming_invoice.internal_reference=content['internal_reference']
							incoming_invoice.save()

							append_to_invoice=invoice_id
							#item_generateProcessingBatchCode=request.query_params.get('generateProcessingBatchCode','')
							#if not item_generateProcessingBatchCode:
							#	item_generateProcessingBatchCode=generateProcessingBatchCode(invoice_id, 'NV')

						else:
							reply['detail']=_('ErrorUneditableInvoice')
							append_to_invoice=0


				else:
					reply['detail']=createErrorDataJSON(serializer.errors)

			else:
				
				reply['detail']=_('ErrorIncomingItemsInvalidInvoice')

		

			registered_items_q=None
			if append_to_invoice>0:
				#add items ok
				item_generateProcessingBatchCode=generateProcessingBatchCode(append_to_invoice, 'NV')

				try:
					
					items=data['items'] #serialer alreayd jsoned it
					items = json.loads(items)

					#items is a list of dictionary items so we add items now. We are looping just in case they change their mind from single item to batch item processing.

					save_items=[]

					for item in items:
						
						item_details=item #dictionary
						
						#get product information here. If it is consumable, add it as it is. Else, generate it in detail creating tags
						product_detail=logisticProductInformation(item_details['pro_id']) #a dictionary.

						if product_detail:
							#the product does exist but is it active?
							store=item_details['store']

							life_span=product_detail['lasts_for_years']
							
							

							if product_detail['active']==1 and Store.objects.filter(pk=store,active=1).exists():
								#do we have a store first
								
							
								#is it consumable or not?
								brand_id=registerNewProductBrand(item_details['brand_name'],request.user.id)
								manf_id=registerNewProductManafacturer(item_details['manf_name'], request.user.id)
								product_properties={  'collection_id':item_generateProcessingBatchCode,'placed_in_store_id':store,'invoice_id':append_to_invoice,'product_id':item_details['pro_id'],'brand_id':brand_id,'manf_id':manf_id,'price':item_details['price'],'arrival_status':'New','processedby_id':request.user.id,'arrivedon':data['processedon'],'current_status':'New', 'manf_serial':None,'institution_code':None    }
								if product_detail['kind'].lower()=='consumable':
									product_properties['tag']=None
									product_properties['expire_on']=item_details['expiry_date']
									product_properties['quantity']=item_details['quantity']
									

									item_info=IncomingItem(**product_properties)
									save_items.append(item_info)
									

									
								else:
									'''
									it is non-consumable. So generate internal/system tags for each item. e.g. quantity can be 7. Generate those 7 tags and return them to front end
									'''
									total_items=item_details['quantity']
									try:
										total_items=int(total_items)
									except:
										total_items=0

									asset_code=product_detail['category__asset_code']
									#generate tags now
									

									for counter in range(total_items):
										prod_ppty=product_properties
										tag=generateProductTag(append_to_invoice, asset_code)
										prod_ppty['tag']=tag
										prod_ppty['quantity']=1
										prod_ppty['expire_on']=None
										item_info=IncomingItem(**prod_ppty)
										save_items.append(item_info)
				
					
					if save_items:
						add_items=IncomingItem.objects.bulk_create(save_items)
						if add_items:
							#put to store. we need id
							registered_items_q=IncomingItem.objects.filter(collection_id=item_generateProcessingBatchCode,invoice_id=append_to_invoice)
							if registered_items_q:
								into_store_items=[]
								added_products=[]
								registered_items=list(registered_items_q)
								for item in registered_items:
									
									put_into_store=ItemInStore(quantity=item.quantity,item_id=item.id,store_id=item.placed_in_store_id,current_status=item.current_status,processedby_id=user_id,arrivedon=item.arrivedon)

									into_store_items.append(put_into_store)
								

									added_products.append({
										'itemid':item.id,
										'tag':item.tag,
										'quantity':item.quantity
										})

								#do we have items?
								if into_store_items:
									fill_store=ItemInStore.objects.bulk_create(into_store_items)
									status=200
									reply['items']=added_products
									reply['invoice_id']=append_to_invoice
									reply['item_generateProcessingBatchCode']=item_generateProcessingBatchCode
									reply['detail']=_('IncomingItemAdded')
								else:
									reply['detail']=_('ErrorAddNewItemRetry')
				
				except:
					reply['detail']=_('ErrorIncomingInvoiceAddError')
					if registered_items_q!=None:
						registered_items_q.delete()
					if invoice_id==0 and invoice:
						invoice.delete()
				
				

				

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class EditIncomingInvoice(APIView):
	'''
	Request information of an invoice to be edited. An invoice cant be edited if it is a month old
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_incominginvoice'])

		if have_right:
			#get the info now
			try:
				reply['editable_status']=0
				invoice=IncomingInvoice.objects.values('id','processedon','provider_id','provider__name','provider__kind','internal_reference','provider_reference').get(pk=invoice_id)
				#now get all the items.
				

				if not invoiceIsEditable(invoice['processedon']):
					reply['tip']=_('ErrorUneditableInvoice')
					reply['editable_status']=2
				else:
					reply['editable_status']=1

				reply['invoice']=invoice




				reply['items']=list(IncomingItem.objects.filter(invoice_id=invoice_id).annotate(store_name=F('placed_in_store__name'),store=F('placed_in_store_id'),pro_id=F('product_id'),cat_id=F('product__category_id'),brand_name=F('brand__name'),manf_name=F('manf__name'),expiry_date=F('expire_on'),   pro_name=Concat('product__name',Value('/'),'product__category__name', output_field=CharField())).values('id','pro_name','brand_name','manf_name','tag','expiry_date','quantity','price','institution_code','manf_serial','arrival_status','pro_id','cat_id','store','store_name'))
				status=200
			except:
				reply['detail']=_('ErrorIncomigInvoiceMissing')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

	def post(self,request,invoice_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_incominginvoice'])

		if have_right:
			data=request.data
			

	
			
			try:
				incoming_invoice=IncomingInvoice.objects.get(pk=invoice_id)

				if invoiceIsEditable(incoming_invoice.processedon):
					serializer=IncomingInvoiceSerializer(data=data,current_id=invoice_id,only_invoice=1)
					if serializer.is_valid():
						content=serializer.validated_data
						
						
						incoming_invoice.provider_id=content['provider']
						incoming_invoice.processedon=content['processedon']
						incoming_invoice.provider_reference=content['provider_reference']

						incoming_invoice.internal_reference=content['internal_reference']
						incoming_invoice.save()
					
						status=200
						reply['detail']=_('InvoiceInformationUpdateOK')

					else:
						reply['detail']=createErrorDataJSON(serializer.errors)


					

				else:
					reply['detail']=_('ErrorUneditableInvoice')
					append_to_invoice=0
			
			
			except:
				reply['detail']=_('ErrorIncomingItemsInvalidInvoice')
			
		
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)





class EditItem(APIView):
	'''
	Edit an item information. Note quantity is a determinant factor here.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,invoice_id,item_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_incomingitem'])

		if have_right:

			try:

				item=IncomingItem.objects.get(invoice_id=invoice_id,pk=item_id)
				original_quantity=float(item.quantity)
				original_tag=item.tag


				new_price=request.data.get('price',0)
				new_quantity=request.data.get('quantity',1)
				product=request.data.get('pro_id',0)
				manf=request.data.get('manf','Unknown')
				brand=request.data.get('brand','Unknown')
				expiry_date=request.data.get('expiry_date','')
				manf_serial=request.data.get('manf_serial','')
				institution_code=request.data.get('institution_code','')
				

				
				new_quantity=float(new_quantity)
				

				if new_quantity==0:
					reply['detail']=_('ErrorQuantityMustBeProvided')

				else:
					#quantity is given correctly


					change=True
							
					#get product information here. If it is consumable, add it as it is. Else, generate it in detail creating tags
					product_detail=logisticProductInformation(product) #a dictionary.

					if product_detail:
						#the product does exist but is it active?
						

						if product_detail['active']==1:
							#do we have a store first
							
						
							#is it consumable or not?
							brand_id=registerNewProductBrand(brand,request.user.id)
							manf_id=registerNewProductManafacturer(manf, request.user.id)
							product_properties={'product_id':product,'brand_id':brand_id,'manf_id':manf_id,'price':new_price,'manf_serial':manf_serial,'institution_code':institution_code}
							
							if product_detail['kind'].lower()=='consumable':
								#the product type sent is consumable. So the total number of given items in the past for the item
								total_given=OutgoingItem.objects.filter(item_id=item.id,invoice__direction='Direct').aggregate(total=Sum('given_quantity'))
								#so far, we have given this much items. Now the new quantity must not be less than that.
								if new_quantity<total_given:
									reply['detail']=_('ErrorQuantityMisMatch') % {'existing':str(total_given),'new':str(new_quantity)}
									change=False
								else:
									product_properties['tag']=None
									product_properties['expire_on']=expiry_date
									product_properties['quantity']=new_quantity

								
							else:
								#it is non-consumable. hence we need to generate tag for the item, it didnt have already No matter how many quantities are specified,
								#it will always be resetted to 1 here. Only if it does not have existing tag tho.
								if original_tag=='':
									asset_code=product_detail['category__asset_code']
									new_tag=generateProductTag(invoice_id, asset_code)
									product_properties['tag']=new_tag

								product_properties['expire_on']=None
								product_properties['quantity']=1

							if change:

								for field in product_properties:
									setattr(item, field, product_properties[field])

								item.save()

								status=200
								if product_properties.get('tag','')!='':
									reply['tag']=product_properties['tag']
								reply['expiry_date']=product_properties['expire_on']
								reply['quantity']=product_properties['quantity']
								reply['detail']=_('ItemInfoUpdateOk')
				
			except:
				reply['detail']=_('ErrorIncomingItemNotFound')

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	

				
					



class DeleteItem(APIView):
	'''
	Delete an item. Remove an item if it has no any history.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,invoice_id,item_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_incomingitem'])

		if have_right:
			try:
				item=IncomingItem.objects.get(invoice_id=invoice_id,pk=item_id)
				#see history in outgoing item and maintance history
				if OutgoingItem.objects.filter(item_id=item_id).exists():
					reply['detail']=_('ErrorDeleteIncomingOutgoingExists')
				else:
					ItemInStore.objects.filter(item_id=item_id).delete()
					item.delete()
					status=200
					reply['detail']=_('ItemDeletedSucessfully')
			except:
				reply['detail']=_('ErrorIncomingItemNotFound')

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)








class PrintableIncomingInvoice(APIView):
	'''
	Print the invoice of an incoming item
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,option,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_print_purchase_invoice'])

		if have_right:
			try:
				reply['invoice_info']=IncomingInvoice.objects.values('processedby__first_name','processedby__last_name','system_id','internal_reference','provider_reference','processedon','createdon','provider__name','provider__phone','provider__email','provider__identification','provider__address').get(pk=invoice_id)
				
				product_information=productInformation()
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']

				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				if option=='detailed':
					items=IncomingItem.objects.filter(invoice_id=invoice_id).values('brand__name','manf__name','product__name','product__measurement_unit','price','expire_on','tag','quantity').order_by('product__name',)
				else:
					items=IncomingItem.objects.filter(invoice_id=invoice_id).values('brand__name','manf__name','product__name','product__measurement_unit','price').annotate(total_items=Sum('quantity')).order_by('product__name')

				reply['items']=list(items)
				status=200
			except:
				reply['detail']=_('ErrorInvoiceMissing')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class PrintableOutgoingInvoice(APIView):
	'''
	Print the invoice of the distribution of items. Receipent can be employee or department. Hence use WHEN clause here
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,option,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_print_distribution_invoice'])

		if have_right:
			try:
			#reply['invoice_info']=OutgoingInvoice.objects.values('give_to__employee__user__first_name','give_to__employee__user__last_name','give_to__employee__phone','give_to__employee__user__email','give_to__employee__company_id','give_to__job__name','give_to__head__name','give_to__division__name','give_to__department__name','give_to__unit__name').get(pk=invoice_id,direction='Direct')
			#reply['invoice_info']=OutgoingInvoice.objects.values('processedby__first_name','processedby__last_name','system_id','internal_reference','processedon','createdon','give_to__employee__user__first_name','give_to__employee__user__last_name','give_to__employee__phone','give_to__employee__user__email','give_to__employee__company_id','give_to__job__name','give_to__head__name','give_to__division__name','give_to__department__name','give_to__unit__name').get(pk=invoice_id,direction='Direct')

				invoice_info = OutgoingInvoice.objects.annotate(
					reciepent_name=Case(

					When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
					When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
					When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
					When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
					When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
					When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
					
					output_field=CharField())).values('id','processedby__first_name','receipent_type','processedby__last_name','system_id','internal_reference','processedon','createdon','reciepent_name','request_invoice_id').get(pk=invoice_id,direction='Direct')

				records = RequestInvoice.objects.values('system_id','processedon','processedby__first_name','processedby__last_name').get(pk=invoice_info['request_invoice_id'])
				
				invoice_info['requestedby']=','.join([records['processedby__last_name'],records['processedby__first_name']])
				invoice_info['requestedon']=records['processedon']
				invoice_info['requestedcode']=records['system_id']

				product_information=productInformation()

				reply['invoice_info']=invoice_info
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				if option=='detailed':
					items=OutgoingItem.objects.filter(invoice_id=invoice_id).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price','item__expire_on','item__tag','given_quantity','given_status','item__manf_serial','item__institution_code').order_by('item__product__name',)
				else:
					items=OutgoingItem.objects.filter(invoice_id=invoice_id).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price').annotate(total_items=Sum('given_quantity')).order_by('item__product__name')

				reply['items']=list(items)
				status=200
			except:
				reply['detail']=_('ErrorInvoiceMissing')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class IncomingInvoicesList(APIView):
	'''
	List of Incoming Invoices
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_purchases_invoices'])

		if have_right:

			filters={}

			

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

			rlrcid=request.query_params.get('rlrcid','').strip() #the invoice that contains this specific item


			
			
			stockedon_compare=dateQueryBuilder('processedon',stocked_portion_option,stocked_on1,stocked_on2,stocked_option)

			products=csvFromUrlToNumbers(products,num='int',ignore_zero=True)

			supplier_kinds=csvFromUrlToNumbers(supplier_kinds,num='str')

			if supplier_kinds:
				filters['provider__kind__in']=supplier_kinds


			if rlrcid:
				filters['incoming_item_invoice__institution_code']=rlrcid
			

			if products:
				filters['incoming_item_invoice__product_id__in']=products

			suppliers=csvFromUrlToNumbers(suppliers,ignore_zero=True)

			if suppliers:
				filters['provider_id__in']=suppliers

		

			if system_id:
				filters['system_id']=system_id

			if provider_reference:
				filters['provider_reference']=provider_reference

			if  internal_reference:
				filters['internal_reference']=internal_reference

			if stockedon_compare:
				filters[stockedon_compare[0]]=stockedon_compare[1]
				#for month equal, we have additional data.
				if len(stockedon_compare)==4:
					filters[stockedon_compare[2]]=stockedon_compare[3]




			records=IncomingInvoice.objects.filter(**filters).values('id','system_id','provider__name','provider__identification','internal_reference','processedon','processedby__first_name','processedby__last_name').annotate(total_price=Sum('incoming_item_invoice__price')).order_by('-id',)
			status=200
			try:

				page=request.query_params.get('page',1)
				paginator=Paginator(records,appsettings.INVOICES_PER_PAGE)
				data=paginator.page(page)

			except PageNotAnInteger:
				data=paginator.page(1)
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				reply['detail']=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.INVOICES_PER_PAGE
				reply['current_page']=page





			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)




class NewOutgoing(APIView):
	'''
	Items are given from the store here. Only Logistic people do so.

	NOTE: NO MORE IN USE. But here for incase stockout can happen without a request.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		

		have_right=userIsPermittedTo(request.user.id,['add_outgoinginvoice'])

		if have_right:
			data=request.data
			serializer=OutgoingInvoiceSerializer(data=data)
			if serializer.is_valid():

				content=serializer.validated_data

				system_id=generateInvoiceCode(kind='OT')

				fields={'receipent_type': content['give_to_type'],'give_to_id':None,'head_id':None,'department_id':None,'division_id':None,'unit_id':None,  'system_id':system_id,'direction':'Direct','note':content['note'],'processedon':content['processedon'],'processedby_id':request.user.id,'internal_reference':content['internal_reference']}


				if content['give_to_type']=='Employee':
					fields['give_to_id']=content['give_to']

				elif content['give_to_type']=='Head':
					fields['head_id']=content['give_to']

				elif content['give_to_type']=='Department':
					fields['department_id']=content['give_to']

				elif content['give_to_type']=='Division':
					fields['division_id']=content['give_to']

				elif content['give_to_type']=='Unit':
					fields['unit_id']=content['give_to']

				elif content['give_to_type']=='Office':
					fields['office_id']=content['give_to']


				invoice=OutgoingInvoice(**fields )
				invoice.save()
				if invoice:

					

					try:
					
						items=content['items'] #serialer alreayd jsoned it
						items = json.loads(items)
						item_generateProcessingBatchCode=generateProcessingBatchCode(invoice.id, 'OV')

						#items is a list of dictionary items so we add items now
						save_items=[]
						rejected_products=[]
						for item in items:
							
							item_details=item #dictionary



							instore_id=item_details['iteminstoreid']
							needed_quantity=float(item_details['quantity'])

							item_instore_info=ItemInStore.objects.get(pk=instore_id)

							current_quantity=float(item_instore_info.quantity)

							give_item=OutgoingItem(processedby_id=request.user.id,given_status=item_instore_info.current_status,ownership_status=1,collection_id=item_generateProcessingBatchCode, given_quantity=needed_quantity, invoice_id=invoice.id,item_id=item_instore_info.item_id,given_from_store_id=item_instore_info.store_id)
							save_items.append(give_item)

							remain_quantity=current_quantity - needed_quantity
							if remain_quantity<=0:
								item_instore_info.delete()


						#check if items were ok?
						if save_items:
							#we hvae products to save of course
							OutgoingItem.objects.bulk_create(save_items)
							


							reply['detail']=_('OutgoingInvoiceAddOk')
							reply['new_id']=invoice.id
							status=200
						else:
							reply['detail']=_('ErrorOutgoingInvoiceAddError')
							invoice.delete()
							
					
					except:
						reply['detail']=_('ErrorOutgoingInvoiceAddError')
						if invoice:
							invoice.delete()
					

					
					
				else:
					reply['detail']=_('ErrorOutgoingInvoiceAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ProcessRequest(APIView):
	'''
	

	Process requests that were made by clients
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		

		have_right=userIsPermittedTo(request.user.id,['add_outgoinginvoice'])

		if have_right:
			data=request.data
			serializer=ProcessRequestSerializer(data=data)
			if serializer.is_valid():

				content=serializer.validated_data

				request_data=content['request_data']

				#content contains requested_invoice that refers to the requested invoice nows

				system_id=generateInvoiceCode(kind='OT')

				fields={'request_invoice_id':request_data.id,'system_id':system_id,'direction':'Direct','note':content['note'],'processedon':content['processedon'],'processedby_id':request.user.id,'internal_reference':content['internal_reference']}

				fields['head_id']=request_data.head_id
				fields['department_id']=request_data.department_id
				fields['unit_id']=request_data.unit_id
				fields['division_id']=request_data.division_id
				fields['give_to']=request_data.give_to
				fields['office_id']=request_data.office_id
				fields['receipent_type']=request_data.receipent_type

					

				invoice=OutgoingInvoice(**fields )
				invoice.save()
				if invoice:

					

					try:
					
						items=content['items'] #serialer alreayd jsoned it
						items = json.loads(items)
						item_generateProcessingBatchCode=generateProcessingBatchCode(invoice.id, 'OV')

						#items is a list of dictionary items so we add items now
						save_items=[]
						rejected_products=[]

						

						delete_from_store=[] #remove non-consumables from the store or finished consuambles
						update_consumeables=[]#for consumbles, just change the quantity

						for item in items:
							
							item_details=item #dictionary



							instore_id=item_details['iteminstoreid']
							needed_quantity=float(item_details['quantity'])

							item_instore_info=ItemInStore.objects.values('item__product__kind','current_status','quantity','item_id','store_id','arrivedon').get(pk=instore_id)

							current_quantity=float(item_instore_info['quantity'])

							

							if item_instore_info['item__product__kind']=='Consumable':
								if current_quantity>=needed_quantity:

									give_item=OutgoingItem(processedby_id=request.user.id,given_status=item_instore_info['current_status'],ownership_status=1,collection_id=item_generateProcessingBatchCode, given_quantity=needed_quantity, invoice_id=invoice.id,item_id=item_instore_info['item_id'],given_from_store_id=item_instore_info['store_id'],arrived_to_store=item_instore_info['arrivedon'])
									save_items.append(give_item)

									remain_quantity=current_quantity - needed_quantity

									if remain_quantity<=0:
										delete_from_store.append(instore_id)
									else:
										update_consumeables.append({'instoreid':instore_id,'quantity':remain_quantity})
									
			
							else:

								give_item=OutgoingItem(processedby_id=request.user.id,given_status=item_instore_info['current_status'],ownership_status=1,collection_id=item_generateProcessingBatchCode, given_quantity=1, invoice_id=invoice.id,item_id=item_instore_info['item_id'],given_from_store_id=item_instore_info['store_id'],arrived_to_store=item_instore_info['arrivedon'])
								save_items.append(give_item)
								delete_from_store.append(instore_id)

								

						#check if items were ok?
						if save_items:
							#we hvae products to save of course
							OutgoingItem.objects.bulk_create(save_items)

							#any items to delete now?
							if delete_from_store:
								deleteable_items=ItemInStore.objects.filter(pk__in=delete_from_store)
								deleteable_items.delete()


							#add non consaumbles sould they exist:
							if update_consumeables:
								save_instore_items=[]
								for item in update_consumeables:
									pkid=item['instoreid']
									quantity=item['quantity']
									item=ItemInStore.objects.get(pk=pkid)
									item.quantity=quantity
									item.save()


						


							reply['detail']=_('OutgoingInvoiceAddOk')
							reply['new_id']=invoice.id
							status=200
							request_data.confirmed=1
							request_data.save()
						else:
							reply['detail']=_('ErrorOutgoingInvoiceAddError')
							invoice.delete()
							
					
					except:
						status=400
						reply['detail']=_('ErrorOutgoingInvoiceAddError')
						if invoice:
							invoice.delete()
					
					
					

					
					
				else:
					reply['detail']=_('ErrorOutgoingInvoiceAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)
class NewRequest(APIView):
	'''
	Employee or entity making a request here
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		

		have_right=userIsPermittedTo(request.user.id,['add_requestinvoice'])

		notify_email=False

		if have_right:
			data=request.data
			serializer=RequestInvoiceSerializer(data=data)
			if serializer.is_valid():

				content=serializer.validated_data

				system_id=generateInvoiceCode(kind='RQ')
				today=date.today()

			

				fields={  'receipent_type': content['give_to_type'],'give_to_id':None,'office_id':None, 'head_id':None,'department_id':None,'division_id':None,'unit_id':None,  'system_id':system_id,'processedon':today,'processedby_id':request.user.id}


				if content['give_to_type']=='Employee':
					fields['give_to_id']=content['give_to']

				elif content['give_to_type']=='Head':
					fields['head_id']=content['give_to']

				elif content['give_to_type']=='Department':
					fields['department_id']=content['give_to']

				elif content['give_to_type']=='Division':
					fields['division_id']=content['give_to']

				elif content['give_to_type']=='Unit':
					fields['unit_id']=content['give_to']

				elif content['give_to_type']=='Office':
					fields['office_id']=content['give_to']


				invoice=RequestInvoice(**fields )
				invoice.save()
				if invoice:

					

					try:
					
						products=content['products'] #serialer alreayd jsoned it
						
						
						#items is a list of dictionary items so we add items now
						save_items=[]
						rejected_products=[]
						for product in products:
							
							product_details=product #dictionary



							product_id=product_details['productid']
							requested_quantity=float(product_details['quantity'])

							

							request_item=RequestedItem(requested_quantity=requested_quantity, invoice_id=invoice.id,product_id=product_id)
							save_items.append(request_item)

							


						#check if items were ok?
						if save_items:
							#we hvae products to save of course
							RequestedItem.objects.bulk_create(save_items)
							
							reply['detail']=_('RequestMadeOk')
							reply['new_id']=invoice.id
							status=200
							notify_email=True
						else:
							reply['detail']=_('ErrorMakingRequest')
							invoice.delete()
							
					
					except:
						reply['detail']=_('ErrorMakingRequest')
						notify_email=False
						if invoice:
							invoice.delete()


					#should we notify logistics people
					if notify_email:
						
						#get logistic people with the right to accept notification
						logistic_people=usersWithPermission(['email_get_request_notification'])
						
						if logistic_people:
							#we have people. just extract their emails here from the list
							emails=[x.get('email') for x in logistic_people]
							
							try:
								emailNewRequestNotification(lang=settings.LANGUAGE_CODE,emails=emails,req_by=' , '.join([request.user.last_name,request.user.first_name]),req_code=system_id,req_date=str(today))
							
							except:
								status=200
								reply['detail']=_('RequestMadeOkErrorEmailing')
					

					
					
				else:
					reply['detail']=_('ErrorMakingRequest')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class MyRequests(APIView):
	'''
	What requests have i initated? For me or any other HR Entity. Show top 100
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=200

		
		records = RequestInvoice.objects.annotate(
			reciepent_name=Case(

			When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
			When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
			When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
			When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
			When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
			When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
			

			output_field=CharField())).filter(processedby_id=request.user.id).values('id','receipent_type','system_id','processedon','reciepent_name','confirmed').order_by('-id',)

		try:
					
			page=request.query_params.get('page',1)
			paginator=Paginator(records,appsettings.INVOICES_PER_PAGE)
			data=paginator.page(page)
		except PageNotAnInteger:
			data=paginator.page(1)
		except EmptyPage:
			data=paginator.page(paginator.num_pages)

		except:
			data=None
			status=400
			reply['detail']=(_('InvalidPath'))

		if status==200:
			reply['detail']=list(data)
			reply['total_num_of_pages']=paginator.num_pages
			reply['total_rows_found']=paginator.count
			reply['total_per_page_allowed']=appsettings.INVOICES_PER_PAGE
			reply['current_page']=page


		reply['detail']=list(records)


		return JsonResponse(reply,status=status)


class ClientRequests(APIView):
	'''
	Requets made by clients
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_outgoinginvoice'])

		if have_right:
			filters={}
			option=request.query_params.get('option',2)

			try:
				option=int(option)
			except:
				option=2

			if option not in [1,2,0]:
				option=2

			if option in [0,1]:
				filters['confirmed']=option

		
			records = RequestInvoice.objects.annotate(
				reciepent_name=Case(

				When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
				When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
				When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
				When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
				When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
				When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
				

				output_field=CharField())).filter(**filters).values('id','receipent_type','system_id','processedon','reciepent_name','confirmed','processedby__last_name','processedby__first_name','outgoing_request__id').order_by('-id',)

			try:
						
				page=request.query_params.get('page',1)
				paginator=Paginator(records,appsettings.INVOICES_PER_PAGE)
				data=paginator.page(page)
				status=200
			except PageNotAnInteger:
				data=paginator.page(1)
				status=200
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				reply['detail']=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.INVOICES_PER_PAGE
				reply['current_page']=page


			reply['detail']=list(records)

		else:
			reply['detail']=_('NoReply')


		return JsonResponse(reply,status=status)


class ClientRequestDetail(APIView):
	'''
	Information about a sepcific request
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_outgoinginvoice'])

		if have_right:
			

			try:
			
		
				reply['invoice'] = RequestInvoice.objects.annotate(
					reciepent_name=Case(

					When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
					When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
					When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
					When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
					When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
					When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
					

					output_field=CharField())).values('id','receipent_type','system_id','processedon','reciepent_name','confirmed','processedby__last_name','processedby__first_name','outgoing_request__id').get(pk=invoice_id)

				reply['items']=list(RequestedItem.objects.filter(invoice_id=invoice_id).values('id','product_id','product__name','requested_quantity','product__measurement_unit').order_by('product__name'))
				status=200
			except:
				reply['detail']=_('ErrorRequestsFormMissing')
			

		else:
			reply['detail']=_('NoReply')


		return JsonResponse(reply,status=status)


class RevokeRequest(APIView):
	'''
	Revoke a request made earlier
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		allow_view=False

		have_right=userIsPermittedTo(request.user.id,['delete_requestinvoice'])
		if have_right:
			try:
				invoice_id=request.data.get('id',0)
				invoice=RequestInvoice.objects.get(processedby_id=request.user.id,pk=invoice_id)
				if invoice.confirmed==0:
					invoice.delete()
					status=200
					reply['detail']=_('RequestRevokedSuccessfully')
				else:
					reply['detail']=_('ErrorRequestRevokeProcessedAlready')

						
			
			except:
				reply['detail']=_('ErrorRequestsFormMissing')

		else:
			reply['detail']=_('NoReply')

		return JsonResponse(reply,status=status)

class PrintableRequestInvoice(APIView):
	'''
	Invoice request. Me owner of the invoice or a person with permission can print it out. This is for unconfirmed only.
	source d request. i=>indrect 9i.e. invoice_id is from OutgoingInvoice
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,source='d',format=None):
		reply={}
		status=400

		allow_view=False

		try:
			filters={}

			if source.lower()=='d':
				filters['pk']=invoice_id
			else:
				filters['outgoing_request__id']=invoice_id

			records = RequestInvoice.objects.annotate(
				reciepent_name=Case(

				When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
				When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
				When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
				When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
				When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
				When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
				

				output_field=CharField())).values('id','receipent_type','system_id','processedon','reciepent_name','confirmed','processedby_id','processedby__first_name','processedby__last_name').get(**filters)
			#before we go on now, get the owner of te invoice and see if permission exists infact
			
			owner_id=records['processedby_id']
			if request.user.id!=owner_id:
				#not owner. So, does this person have the right to view te request/
				have_right=userIsPermittedTo(request.user.id,['extra_can_print_requests_form'])
				if have_right:
					allow_view=True
			else:
				allow_view=True

			if allow_view:
				#get the data now.
				reply['invoice_info']=records
				requested_items=list(RequestedItem.objects.filter(invoice_id=records['id']).values('product__name','requested_quantity','product_id','product__measurement_unit').order_by('product__name'))
				#now if processed, get the items that were processed here
				requested_items_template=[]
				for i in requested_items:
					requested_items_template.append(
						{'produt_name': i['product__name'],'requested_quantity':i['requested_quantity'],'product_id':i['product_id'],'approved_quantity':'','measure':i['product__measurement_unit']}

						)

				if records['confirmed']==1:
				
					stockout_items=list(OutgoingItem.objects.filter(invoice__request_invoice_id=invoice_id).values('item__product_id').annotate(total_items=Sum('given_quantity')).order_by('item__product_id'))
			
					for item in stockout_items:
						total_items=item['total_items']
						product_id=item['item__product_id']
						#find it in template above and update approved_quantity
						for i, dic in enumerate(requested_items_template):
							if dic['product_id']==product_id:
								requested_items_template[i]['approved_quantity']=total_items
								break

				reply['items']=list(requested_items_template)
				product_information=productInformation()
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);

				status=200
				
			else:
				reply['detail']=_('NoRight')
			
					

		
		except:
			reply['detail']=_('ErrorRequestsFormMissing')

		return JsonResponse(reply,status=status)


class SearchItems(APIView):
	'''
	All can see items that are in store.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,give,format=None):
		reply={}
		status=200

		category=request.query_params.get('cat','')
		product=request.query_params.get('product','')


		try:
			category=int(category)
		except:
			category=0


		try:
			product=int(product)
		except:
			product=0

		filters={}


		if product>0:
			#a product is selected
			filters['item__product_id']=product

		if category>0:
			filters['item__product__category_id']=category

		if give.lower()=='yes':
			filters['store__service']='Distribution'


		records=ItemInStore.objects.filter(**filters).values('id','current_status','store__name','item__brand__name','item__manf__name','item__product__name','item__product_id','item__price','item__expire_on','quantity','item__product__kind','item__manf_serial','item__institution_code').order_by('-item__product__name')

		try:
					
			page=request.query_params.get('page',1)
			paginator=Paginator(records,appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS)
			data=paginator.page(page)
		except PageNotAnInteger:
			data=paginator.page(1)
		except EmptyPage:
			data=paginator.page(paginator.num_pages)

		except:
			data=None
			status=400
			reply['detail']=(_('InvalidPath'))

		if status==200:
			reply['detail']=list(data)
			reply['total_num_of_pages']=paginator.num_pages
			reply['total_rows_found']=paginator.count
			reply['total_per_page_allowed']=appsettings.APPSET_NUMBER_OF_INSTORE_ITEMS
			reply['current_page']=page

		return JsonResponse(reply,status=status)			



		
class OutgoingInvoicesList(APIView):
	'''
	List of outgoing Invoices
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_distribution_invoices'])

		if have_right:

			filters={}

			

			suppliers=request.query_params.get('suppliers','').strip() #csv list
			kind=request.query_params.get('kinds','').strip() #csv list of nature of the invocie (unded, purchased)
			supplier_kinds=request.query_params.get('supplier_kinds','').strip()
			system_id=request.query_params.get('system_id','').strip()
			employee=request.query_params.get('employee','').strip()
			internal_reference=request.query_params.get('internal_ref','').strip()
			
			stocked_on1=request.query_params.get('done_date1')
			stocked_on2=request.query_params.get('done_date2')
			stocked_portion_option=request.query_params.get('done_portion','y')
			stocked_option=request.query_params.get('done_date_option','e')

			direction=request.query_params.get('direction','').lower().strip()

			if direction in ['direct','transfer']:
				filters['direction']=direction

		

			products=request.query_params.get('products','').strip()

			heads=request.query_params.get('heads','').strip()
			deps=request.query_params.get('deps','').strip()
			divisions=request.query_params.get('divisions','').strip()
			units=request.query_params.get('units','').strip()
			jobs=request.query_params.get('jobs','').strip()

			if heads:
				heads=csvFromUrlToNumbers(heads,num='int',ignore_zero=True)
				filters['head_id__in']=heads

			if deps:
				deps=csvFromUrlToNumbers(deps)
				filters['department_id__in']=deps

			if divisions:
				divisions=csvFromUrlToNumbers(divisions)
				filters['divisions_id__in']=divisions

			if units:
				units=csvFromUrlToNumbers(units)
				filters['units_id__in']=units

		
			if jobs:
				jobs=csvFromUrlToNumbers(jobs)
				filters['give_to__position_emp__job_id__in']=jobs
				filters['receipent_type']='Employee'



			#employee



			
		
			stockedon_compare=dateQueryBuilder('processedon',stocked_portion_option,stocked_on1,stocked_on2,stocked_option)

			products=csvFromUrlToNumbers(products,num='int',ignore_zero=True)

			supplier_kinds=csvFromUrlToNumbers(supplier_kinds,num='str')

			if supplier_kinds:
				filters['outgoingitem_outgoinginvoice__item__invoice__provider__kind__in']=supplier_kinds



			

			if products:
				filters['outgoingitem_outgoinginvoice__item__product_id__in']=products

			suppliers=csvFromUrlToNumbers(suppliers,ignore_zero=True)

			if suppliers:
				filters['outgoingitem_outgoinginvoice__item__invoice__provider_id__in']=suppliers

		

			if system_id:
				filters['system_id']=system_id

			if employee:
				filters['give_to__rlrc_id']=employee

			if  internal_reference:
				filters['internal_reference']=internal_reference

			if stockedon_compare:
				filters[stockedon_compare[0]]=stockedon_compare[1]
				#for month equal, we have additional data.
				if len(stockedon_compare)==4:
					filters[stockedon_compare[2]]=stockedon_compare[3]





			#records=OutgoingInvoice.objects.filter(**filters).values('id','system_id','internal_reference','processedon','processedby__first_name','processedby__last_name').order_by('-id',)

			records = OutgoingInvoice.objects.annotate(
				reciepent_name=Case(

				When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
				When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
				When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
				When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
				When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
				When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
				

				output_field=CharField())).filter(**filters).values('id','processedby__first_name','receipent_type','processedby__last_name','system_id','internal_reference','processedon','createdon','reciepent_name','direction').order_by('-id',)




			status=200
			try:

				page=request.query_params.get('page',1)
				paginator=Paginator(records,appsettings.INVOICES_PER_PAGE)
				data=paginator.page(page)

			except PageNotAnInteger:
				data=paginator.page(1)
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				reply['detail']=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.INVOICES_PER_PAGE
				reply['current_page']=page





			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)




class ItemsInPossession(APIView):
	'''
	List of items with an entity. It could be an employee or an hr entity.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,option,show,return_entity_info,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_inpossession_items'])

		if have_right:

			entity_type=request.query_params.get('e_type','Employee').strip().capitalize()
			entity_id=request.query_params.get('e_id','').strip()

			ALLOWED_RECEIPENT_TYPES=[x[0] for x in settings.RECEIPENT_TYPES]

			if entity_type not in ALLOWED_RECEIPENT_TYPES:
				reply['detail']=_('ErrorInvalidEntity')
			else:
				if show not in ['1','2','3']:
					show='1'

				#entity information here now
				entity_info={}
				try:
					detailed_filters={'invoice__receipent_type':entity_type,'ownership_status':1}
					summary_filters={'receipent_type':entity_type,'outgoingitem_outgoinginvoice__ownership_status':1}
					if return_entity_info=='y':
						reply['entity_info']=entityInformation(entity_type, entity_id)

					if entity_type=='Employee':
						#entity_info=Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '), 'user__first_name'),email=F('user__email')).values('full_name','email','phone','id').get(company_id=entity_id)
						detailed_filters['invoice__give_to_id']=entity_id
						summary_filters['give_to_id']=entity_id
					elif entity_type=='Head':
						#entity_info=Head.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
						detailed_filters['invoice__head_id']=entity_id
						summary_filters['head_id']=entity_id
					elif entity_type=="Department":
						#entity_info=Department.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
						detailed_filters['invoice__department_id']=entity_id
						summary_filters['department_id']=entity_id
					elif entity_type=='Division':
						#entity_info=Division.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
						detailed_filters['invoice__division_id']=entity_id
						summary_filters['division_id']=entity_id
					elif entity_type=='Unit':
						#entity_info=Unit.objects.annotate(full_name=F('name'),phone=Value(''),email=Value('')).values('full_name','email','phone','id').get(pk=entity_id)
						detailed_filters['invoice__unit_id']=entity_id
						summary_filters['unit_id']=entity_id
					elif entity_type=='Office':
						detailed_filters['invoice__office_id']=entity_id
						summary_filters['office_id']=entity_id


					if option.lower()=='detailed':
						invoice_id=request.query_params.get('invoice',0).strip()
						invoice_id=int(invoice_id)
						if invoice_id>0:
							detailed_filters['invoice_id']=invoice_id
						

						if show=='2':
							#only consmable
							detailed_filters['item__product__kind']='Consumable'
						elif show=='3':
							detailed_filters['item__product__kind']='Non-consumable'

						
					
						items=OutgoingItem.objects.filter(**detailed_filters).values('id','invoice_id','invoice__system_id','invoice__internal_reference','invoice__processedon','item__product__name','item__brand__name','item__manf__name','given_status','given_quantity','item__institution_code','item__manf_serial' ).order_by('-invoice__processedon',)
						
					else:
						#get invoices registered to the entity instead.
						if show=='2':
							#only consmable
							
							summary_filters['outgoingitem_outgoinginvoice__item__product__kind']='Consumable'
						elif show=='3':

							summary_filters['outgoingitem_outgoinginvoice__item__product__kind']='Non-consumable'


						items=OutgoingInvoice.objects.filter(**summary_filters).values('id','system_id','internal_reference','processedon').annotate(total_items=Count('outgoingitem_outgoinginvoice')).order_by('-invoice__processedon',).order_by('-processedon',)

					reply['detail']=list(items)
					status=200
				except:
					reply['detail']=_('ErrorInvalidEntity')



			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)





class ReturnSpecifiedItems(APIView):
	'''
	Call me when you want to return items. Returns can be from Employee, and HR entities (head->unit)
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400



		have_right=userIsPermittedTo(request.user.id,['add_returniteminvoice'])

		if have_right:
			data=request.data
			serializer=ReturnInvoiceSerializer(data=data)
			if serializer.is_valid():

				content=serializer.validated_data

				system_id=generateInvoiceCode(kind='RT')

				invoice_fields={'return_by_id':None,'head_id':None,'department_id':None,'division_id':None,'unit_id':None,'returner_type':content['return_by_type'],'system_id':system_id,'note':content['note'],'processedon':content['processedon'],'processedby_id':request.user.id,'internal_reference':content['internal_reference'] }
				filters_og={'id':None}
				if content['return_by_type']=='Employee':
					invoice_fields['return_by_id']=content['return_by']
					filters_og['invoice__give_to_id']=content['return_by']
				if content['return_by_type']=='Head':
					invoice_fields['head_id']=content['return_by']	
					filters_og['invoice__head_id']=content['return_by']			
				if content['return_by_type']=='Department':
					invoice_fields['department_id']=content['return_by']
					filters_og['invoice__department_id']=content['return_by']
				if content['return_by_type']=='Division':
					invoice_fields['division_id']=content['return_by']
					filters_og['invoice__division_id']=content['return_by']
				if content['return_by_type']=='Unit':
					invoice_fields['unit_id']=content['return_by']
					filters_og['invoice__unit_id']=content['return_by']
				if content['return_by_type']=='Office':
					invoice_fields['office_id']=content['return_by']
					filters_og['invoice__office_id']=content['return_by']

				invoice=ReturnItemInvoice(**invoice_fields)
				invoice.save()

				return_filters={}

				if invoice:


					try:
					
						items=content['items'] #serialer alreayd jsoned it
						items = json.loads(items)
						item_generateProcessingBatchCode=generateProcessingBatchCode(invoice.id, 'RT')

						#items is a list of dictionary items so we add items now
						save_items=[] #to return back to store
						return_items=[]
						returned_items=[]
						update_items_status=[] #goes to IncomingItem so we maintain its updated status always
						rejected_products=[]

						for item in items:
							
							item_details=item #dictionary

							

							outgoing_item_id=item_details['product_id'] #refers to id in OUtgoingItem model
							return_status=item_details['return_status']
							filters_og['id']=outgoing_item_id

							
							

							outgoing_item_info=OutgoingItem.objects.values('item__product__kind','item_id').get(**filters_og)

							#infact the item is in his possession

							#return if kind is Non-consumle.
							if outgoing_item_info['item__product__kind']=='Non-consumable' and return_status.capitalize() in ['Unknown','Used','New','Defective','Disfunctional']:
								#mark it for deletion yes. Put it back to store first
								item=ItemInStore(store_id=content['store'],item_id=outgoing_item_info['item_id'],current_status=return_status,quantity=1,arrivedon=content['processedon'],processedby_id=request.user.id)
								save_items.append(item)
								returned_items.append(outgoing_item_id)
								return_item=ReturnItem(invoice_id=invoice.id,item_id=outgoing_item_id,collection_id=item_generateProcessingBatchCode,return_to_store_id=content['store'],return_status=return_status)
								return_items.append(return_item)
								update_global_item_status={'id':outgoing_item_info['item_id'],'current_status':return_status}
								update_items_status.append(update_global_item_status)
							



						#check if items were ok?
						if save_items:

							#we hvae products to save of course
							ItemInStore.objects.bulk_create(save_items)
							ReturnItem.objects.bulk_create(return_items)
							#mark the items returned now
							owned_items=OutgoingItem.objects.filter(pk__in=returned_items).update(ownership_status=2)
							#update the status of the items now
							for i in update_items_status:
								incoming_item=IncomingItem.objects.get(pk=i['id'])
								incoming_item.current_status=i['current_status']
								incoming_item.save()

							reply['detail']=_('ReturnInvoiceAddOk')
							reply['new_id']=invoice.id
							status=200
						else:
							reply['detail']=_('ErrorReturnInvoiceAddError')
							invoice.delete()
							
					
					except:
						reply['detail']=_('ErrorReturnInvoiceAddError')
						if invoice:
							invoice.delete()
					
					
					

					
					
				else:
					reply['detail']=_('ErrorOutgoingInvoiceAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ReturnedItemsList(APIView):
	'''
	What items were returned under that specific return invoice?
	Usable to manage retuned items, including undoing or changing the return item return status
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,invoice_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['can_view_returend_items_list'])
		if have_right:
			status=200
			reply['detail']=list(ReturnItem.objects.filter(invoice_id=invoice_id).values('item__item__brand__name','item__item__manf__name','item__item__product__name','item__item__tag','return_status' ,'item__item__manf_serial','item__item__institution_code','id').order_by('item__item__product__name',))

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class TransferedItemsList(APIView):
	'''
	What items were transfered under that specific transfer invoice?
	Usable to manage transfered items, including undoing or changing the transfered item's transfer status
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,invoice_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['can_view_tranfered_items_list'])
		if have_right:
			status=200
			reply['detail']=list(OutgoingItem.objects.filter(invoice_id=invoice_id,invoice__direction="Transfer").values('item__brand__name','item__manf__name','item__product__name','item__tag','given_status' ,'item__manf_serial','item__institution_code','id').order_by('item__product__name',))

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)
						

class StockedOutItemsList(APIView):
	'''
	Which items were stocked out under the same invoice?
	Usable to manage stocked out items, including undoing or changing the status and quantity
	'''
	permission_classes = [TokenHasReadWriteScope]
	def get(self,request,invoice_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['can_view_stocked_out_items_list'])
		if have_right:
			status=200
			reply['detail']=list(OutgoingItem.objects.filter(invoice_id=invoice_id,invoice__direction="Direct").values('item__brand__name','item__manf__name','item__product__name','item__tag','given_status' ,'item__manf_serial','item__institution_code','id','given_quantity','ownership_status','item__product__kind').order_by('item__product__name',))

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class PrintableReturnInvoice(APIView):
	'''
	Print the invoice of the return of items
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,option,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_print_return_invoice'])

		if have_right:
			try:
				reply['invoice_info'] = ReturnItemInvoice.objects.annotate(
					returner_name=Case(

					When(returner_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
					When(returner_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
					When(returner_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
					When(returner_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
					When(returner_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
					When(returner_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('return_by_id')).values('full_name'))),
					
					output_field=CharField())).values('id','processedby__first_name','returner_type','processedby__last_name','system_id','internal_reference','processedon','createdon','returner_name').get(pk=invoice_id)

				product_information=productInformation()
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				if option=='detailed':
					items=ReturnItem.objects.filter(invoice_id=invoice_id).values('item__item__brand__name','item__item__manf__name','item__item__product__name','item__item__product__measurement_unit','item__item__price','item__item__tag','return_status' ,'item__item__manf_serial','item__item__institution_code').order_by('item__item__product__name',)
				else:
					items=ReturnItem.objects.filter(invoice_id=invoice_id).values('item__item__brand__name','item__item__manf__name','item__item__product__name','item__item__product__measurement_unit').annotate(total_items=Count('id')).order_by('item__item__product__name')

				reply['items']=list(items)
				status=200
			except:
				reply['detail']=_('ErrorInvoiceMissing')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class ReturnInvoicesList(APIView):
	'''
	List of return Invoices
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_return_invoices'])

		if have_right:

			filters={}

			
			system_id=request.query_params.get('system_id','').strip()
			employee=request.query_params.get('employee','').strip()
			head=request.query_params.get('head','').strip()
			dept=request.query_params.get('dept','').strip()
			division=request.query_params.get('division','').strip()
			unit=request.query_params.get('unit','').strip()
			internal_reference=request.query_params.get('internal_ref','').strip()
			
			stocked_on1=request.query_params.get('done_date1')
			stocked_on2=request.query_params.get('done_date2')
			stocked_portion_option=request.query_params.get('done_portion','y')
			stocked_option=request.query_params.get('done_date_option','e')

		

			products=request.query_params.get('products','').strip()

			stockedon_compare=dateQueryBuilder('processedon',stocked_portion_option,stocked_on1,stocked_on2,stocked_option)

			products=csvFromUrlToNumbers(products,num='int',ignore_zero=True)
			head=csvFromUrlToNumbers(head,num='int',ignore_zero=True)
			dept=csvFromUrlToNumbers(dept,num='int',ignore_zero=True)
			division=csvFromUrlToNumbers(division,num='int',ignore_zero=True)
			unit=csvFromUrlToNumbers(unit,num='int',ignore_zero=True)




			

			if products:
				filters['returnitem_returninvoice__item__item__product_id__in']=products


			if system_id:
				filters['system_id']=system_id

			if employee:
				filters['return_by__rlrc_id']=employee

			if head:
				filters['head_id__in']=head

			if dept:
				filters['department_id__in']=dept

			if division:
				filters['division_id__in']=division

			if unit:
				filters['unit_id__in']=unit

			if  internal_reference:
				filters['internal_reference']=internal_reference

			if stockedon_compare:
				filters[stockedon_compare[0]]=stockedon_compare[1]
				#for month equal, we have additional data.
				if len(stockedon_compare)==4:
					filters[stockedon_compare[2]]=stockedon_compare[3]

			records = ReturnItemInvoice.objects.annotate(
				returner_name=Case(

				When(returner_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
				When(returner_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
				When(returner_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
				When(returner_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
				When(returner_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
				When(returner_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('return_by_id')).values('full_name'))),
				

				output_field=CharField())).filter(**filters).values('id','processedby__first_name','returner_type','processedby__last_name','system_id','internal_reference','processedon','createdon','returner_name').order_by('-id',)


			status=200
			try:

				page=request.query_params.get('page',1)
				paginator=Paginator(records,appsettings.INVOICES_PER_PAGE)
				data=paginator.page(page)

			except PageNotAnInteger:
				data=paginator.page(1)
			except EmptyPage:
				data=paginator.page(paginator.num_pages)

			except:
				data=None
				status=400
				reply['detail']=(_('InvalidPath'))

			if status==200:
				reply['detail']=list(data)
				reply['total_num_of_pages']=paginator.num_pages
				reply['total_rows_found']=paginator.count
				reply['total_per_page_allowed']=appsettings.INVOICES_PER_PAGE
				reply['current_page']=page
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)




class NewTransfer(APIView):
	'''
	Transfer items between employees. Note the items are not taken.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_make_transfers'])

		if have_right:
			data=request.data
			serializer=TransferInvoiceSerializer(data=data)
			if serializer.is_valid():

				content=serializer.validated_data

				system_id=generateInvoiceCode(kind='TR')

				invoice_fields={'transfered_from_division_id':None,'transfered_from_unit_id':None,'transfered_from_type':content['transfered_from_type'], 'transfered_from_id':None,'transfered_from_head_id':None,'transfered_from_department_id':None,   'give_to_id':None,'head_id':None,'department_id':None,'division_id':None,'unit_id':None,'receipent_type':content['transfered_to_type'],    'system_id':system_id,'direction':'Transfer','note':content['note'],'processedon':content['processedon'],'processedby_id':request.user.id,'internal_reference':content['internal_reference']}
				og_fields={'id':None}
				if content['transfered_from_type']=='Employee':
					invoice_fields['transfered_from_id']=content['transfered_from']
					og_fields['invoice__give_to_id']=content['transfered_from']
				elif content['transfered_from_type']=='Head':
					invoice_fields['transfered_from_head_id']=content['transfered_from']	
					og_fields['invoice__head_id']=content['transfered_from']			
				elif content['transfered_from_type']=='Department':
					invoice_fields['transfered_from_department_id']=content['transfered_from']
					og_fields['invoice__department_id']=content['transfered_from']
				elif content['transfered_from_type']=='Division':
					invoice_fields['transfered_from_division_id']=content['transfered_from']
					og_fields['invoice__division_id']=content['transfered_from']	
				elif content['transfered_from_type']=='Unit':
					invoice_fields['transfered_from_unit_id']=content['transfered_from']
					og_fields['invoice__unit_id']=content['transfered_from']
				elif content['transfered_from_type']=='Office':
					invoice_fields['transfered_from_office_id']=content['transfered_from']
					og_fields['invoice__office_id']=content['transfered_from']


				if content['transfered_to_type']=='Employee':
					invoice_fields['give_to_id']=content['transfered_to']
				elif content['transfered_to_type']=='Head':
					invoice_fields['head_id']=content['transfered_to']				
				elif content['transfered_to_type']=='Department':
					invoice_fields['department_id']=content['transfered_to']
				elif content['transfered_to_type']=='Division':
					invoice_fields['division_id']=content['transfered_to']	
				elif content['transfered_to_type']=='Unit':
					invoice_fields['unit_id']=content['transfered_to']
				elif content['transfered_to_type']=='Office':
					invoice_fields['office_id']=content['transfered_to']


				invoice=OutgoingInvoice(**invoice_fields)
				invoice.save()
				
				if invoice:

					

					try:
					
						items=content['items'] #serialer alreayd jsoned it
						items = json.loads(items)
						item_generateProcessingBatchCode=generateProcessingBatchCode(invoice.id, 'TR')

						#items is a list of dictionary items so we add items now
						save_items=[] #to return back to store
						return_items=[]
						transfered_items=[]
						update_items_status=[] #goes to IncomingItem so we maintain its updated status always
						

						for item in items:
							
							item_details=item #dictionary

							

							outgoing_item_id=item_details['product_id'] #refers to id in OUtgoingItem model
							transfer_status=item_details['transfer_status']
							og_fields['id']=outgoing_item_id

							outgoing_item_info=OutgoingItem.objects.values('item__product__kind','item_id','given_from_store_id','id').get(**og_fields)
							#infact the item is in his possession


							#return if kind is Non-consumle.
							if outgoing_item_info['item__product__kind']=='Non-consumable' and transfer_status.capitalize() in ['Unknown','Used','New','Burned','Defective','Disfunctional']:
								#mark it for deletion yes. Put it back to store first
								give_item=OutgoingItem(transfered_item_id=outgoing_item_info['id'],processedby_id=request.user.id,given_status=transfer_status,ownership_status=1,collection_id=item_generateProcessingBatchCode, given_quantity=1, invoice_id=invoice.id,item_id=outgoing_item_info['item_id'],given_from_store_id=outgoing_item_info['given_from_store_id'])

								save_items.append(give_item)

								transfered_items.append(outgoing_item_id)
								update_global_item_status={'id':outgoing_item_info['item_id'],'current_status':transfer_status}
								update_items_status.append(update_global_item_status)
							



						#check if items were ok?
						if save_items:
							#we hvae products to save of course
							OutgoingItem.objects.bulk_create(save_items) #add the new once
							OutgoingItem.objects.filter(pk__in=transfered_items).update(ownership_status=5) #mark transfered

							
							#update the status of the items now
							for i in update_items_status:
								incoming_item=IncomingItem.objects.get(pk=i['id'])
								incoming_item.current_status=i['current_status']
								incoming_item.save()

							reply['detail']=_('TransferInvoiceAddOk')
							reply['new_id']=invoice.id
							status=200
						else:
							reply['detail']=_('ErrorTransferInvoiceAddError')
							invoice.delete()
							
					
					except:
						reply['detail']=_('ErrorTransferInvoiceAddError')
						if invoice:
							invoice.delete()
					
					

					
					
				else:
					reply['detail']=_('ErrorOutgoingInvoiceAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class PrintableTransferInvoice(APIView):
	'''
	Print the invoice of the transfer of items
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,invoice_id,option,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_print_transfer_invoice'])

		if have_right:
			try:

				reply['invoice_info'] = OutgoingInvoice.objects.annotate(
					transfered_to_name=Case(

					When(receipent_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('head_id')).values('name',))),
					When(receipent_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('department_id')).values('full_name'))),
					When(receipent_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('division_id')).values('full_name'))),
					When(receipent_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('unit_id')).values('full_name'))),
					When(receipent_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('office_id')).values('name'))),
					When(receipent_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('give_to_id')).values('full_name'))),
					
					output_field=CharField()),

					transfered_from_name=Case(

					When(transfered_from_type='Head', then=Subquery(Head.objects.filter(pk=OuterRef('transfered_from_head_id')).values('name',))),
					When(transfered_from_type='Department', then=Subquery(Department.objects.annotate(full_name=Concat('head__name',Value(' - '),'name')).filter(pk=OuterRef('transfered_from_department_id')).values('full_name'))),
					When(transfered_from_type='Division', then=Subquery(Division.objects.annotate(full_name=Concat('department__head__name',Value(' - '),'department__name',Value(' - '),'name')).filter(pk=OuterRef('transfered_from_division_id')).values('full_name'))),
					When(transfered_from_type='Unit', then=Subquery(Unit.objects.annotate(full_name=Concat('division__department__head__name',Value(' - '),'division__department__name',Value(' - ' ),'division__name',Value(' - '),'name')).filter(pk=OuterRef('transfered_from_unit_id')).values('full_name'))),
					When(transfered_from_type='Office', then=Subquery(Office.objects.filter(pk=OuterRef('transfered_from_office_id')).values('name'))),
					When(transfered_from_type='Employee', then=Subquery(Employee.objects.annotate(full_name=Concat('user__last_name',Value(' , '),'user__first_name')).filter(pk=OuterRef('transfered_from_id')).values('full_name'))),
					
					output_field=CharField())



					).values('id','processedby__first_name','transfered_from_type','receipent_type','processedby__last_name','system_id','internal_reference','processedon','createdon','transfered_to_name','transfered_from_name').get(pk=invoice_id,direction='Transfer')

				product_information=productInformation()
				reply['company_name']=product_information['company_name']
				reply['software_name']=product_information['product_name']
				reply['printedby']=','.join([request.user.last_name,request.user.first_name]);
				
				if option=='detailed':
					items=OutgoingItem.objects.filter(invoice_id=invoice_id).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price','item__expire_on','item__tag','given_quantity','given_status').order_by('item__product__name',)
				else:
					items=OutgoingItem.objects.filter(invoice_id=invoice_id).values('item__brand__name','item__manf__name','item__product__name','item__product__measurement_unit','item__price').annotate(total_items=Count('id')).order_by('item__product__name')
				print(str(items.query))
				reply['items']=list(items)
				status=200
			except:
				reply['detail']=_('ErrorInvoiceMissing')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ChangeItemStatus(APIView):
	'''
	Change status of an item. It must be non-consumable and it can be in store, in use. It can also be reported as Lost or if it is currently lost, as other state
	Only logistic person can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,tag,new_status,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_change_item_status'])

		if have_right:
			#get the info now
			try:
				item=IncomingItem.objects.get(tag=tag,product__kind='Non-consumable')
				#item exists ok. Now se the new status. It should be valid kind of course.
				STATUS=[x[0] for x in settings.STATUS]
				if new_status not in STATUS:
					reply['new_status']=_('ErrorStatusChangeInvalidStatus')
				else:
					#change it
					current_status=item.current_status
					arrived_to_store=item.placed_in_store_id
					item.current_status=new_status
					item.save()
					status=200
					reply['detail']=_('StatusUpdatedOk')

					addItemHistory(item.id, 'Status Changed:' + new_status, request.user.id)

					#if the item was previously lost, then put it back to store for retreival
					if current_status=='Lost' and new_status!='Lost':
						put_to_sotre=ItemInStore(quantity=1,arrivedon=date.today(),item_id=item.id,store_id=arrived_to_store,current_status=new_status,processedby_id=request.user.id)
						put_to_sotre.save()
			except:
				reply['detail']=_('ErrorItemMissing')

				
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ReportItemAsLost(APIView):
	'''
	Report a non-consumable item as lost. If the item is currently in store, simply unstore it so it doesnt appear in list of in-store items
	if it is is under someone or an office, auto-return it as Lost.
	Only logisitic can do the action
	'''

	def post(self,request,tag,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_report_lost_items'])

		if have_right:
			#get the info now
			reported_as_lost=False
			try:
				item=IncomingItem.objects.get(tag=tag,product__kind='Non-consumable')
				#item exists ok.
				if item.current_status=='Lost':
					#report a lost item as lost
					reply['detail']=_('ErrorReportItemLostAlreadyLost')
				else:
					#change it
					item.current_status='Lost'
					item.save()
					status=200
					reported_as_lost=True
					reply['detail']=_('StatusUpdatedOk')
					addItemHistory(item.id, 'Lost', request.user.id)
			
			except:
				reply['detail']=_('ErrorItemMissing')

			#now see where it is:
			check_out_goingitem=False
			try:
				instore=ItemInStore.objects.filter(item_id=item.id)
				instore.delete()
			except:
				#it was not found in the store. See if it is in given items
				check_out_goingitem=True


			if check_out_goingitem:
				try:
					ogitem=OutgoingItem.objects.get(item_id=item.id,ownership_status=1)
					#found. Simply set it as Lost here
					ogitem.ownership_status=3
					ogitem.save()
				except:
					pass


				
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class ReportLostItemAsFound(APIView):
	'''
	Report a non-consumable item that was lost as found. When found, its status must be provided.
	If the item was returned as Lost, unreturn it (i.e. put it in possession) then the person in hold of it can return it or not.
	If not, put it back to the provided store.

	new_status is used only if we are putting the item back to store.

	Since the input variables are little, error check is on field by field basis. YOu can define an error message holder if you want
	
	'''

	def post(self,request,tag,store_id,new_status,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_report_found_items'])



		if have_right:
			#get the info now
			
			check_out_goingitem=False
			try:
				item=IncomingItem.objects.get(tag=tag,product__kind='Non-consumable')
				#item exists ok.
				if item.current_status!='Lost':
					#item was not known othave been lost
					reply['detail']=_('ErrorReportItemLostNotLost')
				else:
					#the item is infact reported as lost. See where it was first. But here first, make sure the status is valid.
					STATUS=[x[0] for x in settings.STATUS]
					if new_status not in STATUS:
						reply['new_status']=_('ErrorStatusChangeInvalidStatus')

					else:

						check_out_goingitem=True
			
			except:
				reply['detail']=_('ErrorItemMissing')

			#now see where it is:
			put_back_to_store=False
			if check_out_goingitem:
				try:
					ogitem=OutgoingItem.objects.get(item_id=item.id,ownership_status=3)
					#it was returned as lost
					ogitem.ownership_status=1
					ogitem.given_status=new_status
					ogitem.save()
					status=200
					
					reply['detail']=_('ItemFoundReturnToOwner')
				except:
					#reached here. It was not returned as Lost. Hence make sure the store is valid then put it back
					if not Store.objects.filter(pk=store_id,active=1).exists():
						reply['detail']=_('ErrorInactiveStoreCantPutItems')
					else:
						#store is ok.
						instore=ItemInStore(item_id=item.id,store_id=store_id,current_status=new_status,processedby_id=request.user.id,quantity=1,arrivedon=date.today())
						instore.save()
						if instore:
							status=200
							reply['detail']=_('LostItemReturnedToStore')
						else:
							reply['detail']=_('ErrorReportLostItemAsFound')

			
			#updae status of the item globally now:
			if status==200:
				item.current_status=new_status
				item.save()
				addItemHistory(item.id, 'Found', request.user.id)
			

				
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

