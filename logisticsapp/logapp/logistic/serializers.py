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
from hr.models import Department, Division, Employee, Head, Office, Unit
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from validation.validators import validateCharacters
from tools.checkup import checkEmailFormat, checkPhone
from datetime import date,timedelta #for checking renewal date range.
from dateutil import parser
from app.conf import base as settings
from logistic.models import IncomingInvoice, ItemInStore, OutgoingInvoice, Provider, ProviderKind, RequestInvoice, ReturnItemInvoice
from inventory.models import Store,Product
import json



def HRStructureCheck(kind,hr_id,check_active='No'):
	'''
	Called from various serializers, I check if the particular HR is correct or not.
	'''
	errmsg='';
	filters={'id':hr_id}

	if check_active=='Yes':
		if kind in ['Head','Department','Division','Unit']:
			filters['active']=1

		elif kind in ['Employee']:
			filters['user__is_active']=1

	if kind=='Head':
		#check the head is active:
		if not Head.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')

	elif kind=="Employee":
		if not Employee.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')
			
	elif kind=="Office":
		if not Office.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')


	elif kind=='Department':
		if not Department.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')

	elif kind=='Division':
		if not Division.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')

	elif kind=='Unit':
		if not Unit.objects.filter(**filters).exists():
			errmsg=_('ErrorInvalidEntity')
	else:
		errmsg=_('ErrorInvalidEntity')


	return errmsg;


class RequestInvoiceSerializer(serializers.Serializer):
	'''
	Make sure the request of items by other employees/HR entities is valid
	
	'''
	products=serializers.CharField(max_length=200000,allow_blank=True,required=False)
	give_to=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35) #general receipent id. Its reference is based on receipent type below
	give_to_type=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)


	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(RequestInvoiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		
		products=data.get('products','').strip()
		give_to=data.get('give_to','').strip()
		give_to_type=data.get('give_to_type','').strip().capitalize()
		

		errmsg={}
		#we start with give to type, which determines what we will check
		ALLOWED_RECEIPENT_TYPES=[x[0] for x in settings.RECEIPENT_TYPES]

		if give_to_type not in ALLOWED_RECEIPENT_TYPES:
			errmsg['give_to_type']=_('ErrorRequestUnknownReceipentType')

		else:
			#the receipent is ok. So get give_to type here
			receipent_do_check=False
			try:
				give_to=int(give_to)
				if give_to<=0:
					errmsg['give_to']=_('ErrorRequestUnknownReceipentType')
				else:
					receipent_do_check=True
					
			except:
				errmsg['give_to']=_('ErrorRequestUnknownReceipentType')

			#should we confirm the data of the receipent here?
			if receipent_do_check:
				hr_check_msg=HRStructureCheck(give_to_type,give_to,check_active=1)
				if hr_check_msg:
					errmsg['give_to']=hr_check_msg
				



		#check items to be given now.. Since, it can be database-costly, carry out hte check below if nothing is errorful above:
		
		
		

		if not products:
			errmsg['items']=_('ErrorRequestInvoiceNoItems')
		else:
			#check each.
			products=json.loads(products)
			
			for product in products:
				#get info
				product_details=product #dictionary
				product_id=product_details['productid']
				try:
					quantity=float(product_details['quantity']) #quantity asked
				except:
					quantity=0

				#check if product is valid/active
				if not Product.objects.filter(pk=product_id,active=1).exists():
					errmsg['products']=_('ErrorRequestInvalidProduct')
					break

		if errmsg:
			raise serializers.ValidationError(errmsg)

		else:
			data['products']=products



		return data

class ProviderKindSerializer(serializers.Serializer):
	'''
	Verify information of a kind of supplier is correct
	'''
	name=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=30)#
	



	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ProviderKindSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		name=data.get('name','').strip()
		

		errmsg={}

		if len(name)<2:
			errmsg['name']=_('ErrorLogisticSupplierKindNameTooShort') % {'min': '2'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#is it unique
				exclude={}
				if self.current_row_id>0:
					exclude['id']=self.current_row_id
				if ProviderKind.objects.filter(name=name).exclude(**exclude).exists():
					errmsg['name']=_('ErrorLogisticSupplierKindExists')


		if errmsg:
			raise serializers.ValidationError(errmsg)

	
		return data

class ProviderSerializer(serializers.Serializer):
	'''
	Verify information of a provider/supplier is correct
	'''
	name=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	identification=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	phone=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=13)#
	email=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=35)#
	www=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=255)#
	kind=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=35)#
	address=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=3000)#





	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ProviderSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		name=data.get('name','').strip()
		identification=data.get('identification','')
		phone=data.get('phone','')
		email=data.get('email','')
		www=data.get('www','')
		kind=data.get('kind','').strip().lower()
		address=data.get('address','')

		errmsg={}

		if len(name)<2:
			errmsg['name']=_('ErrorLogisticSupplierNameTooShort') % {'min': '2'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

		#2. Identification

		if identification!=None and len(identification)>5:
			exclude={}
			identification=identification.strip()
			if self.current_row_id>0:
				exclude['id']=self.current_row_id

			if Provider.objects.filter(identification=identification).exclude(**exclude).exists():
				errmsg['identification']=_('ErrorLogisticSupplierIDNotUnique')
			else:
				data['identification']=identification
		else:
			data['identification']=None



		if email!=None:
			email=email.strip()

			if checkEmailFormat(email,required=False)==False:
				errmsg['email']=_('ErrorEmailInvalidOptional')

		else:
			data['email']=''

		if phone!=None and checkPhone(phone)==False:
			errmsg['phone']=_('ErrorPhoneInvalidOptional')

		if address!=None:
			data['address']=address.strip()

		if www!=None or www:
			data['www']=www.strip()


		if not ProviderKind.objects.filter(pk=kind).exists():
			errmsg['kind']=_('ErrorLogisticSupplierInvalidKind')

		if errmsg:
			raise serializers.ValidationError(errmsg)

	
		return data


class IncomingInvoiceSerializer(serializers.Serializer):
	'''
	Make sure the incoming invoice is correct
	'''
	
	processedon=serializers.DateField()
	
	provider=serializers.CharField(max_length=30,allow_blank=True,allow_null=True,required=False)
	provider_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	internal_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	items=serializers.CharField(max_length=200000,allow_blank=True,required=False)


	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.only_invoice=int(kwargs.pop('only_invoice', 0))
		super(IncomingInvoiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		processedon=data.get('processedon','')
		
		provider=data.get('provider','').strip()
		provider_reference=data.get('provider_reference','')
		internal_reference=data.get('internal_reference','')
		items=data.get('items','').strip()
	
		errmsg={}

		
		if processedon:


				
			#convert processedon to date.
			try:
				processedon=parser.parse(str(processedon)).date()
				
				if processedon > date.today():
					
					#raise forms.ValidationError(_('Invalid birth date - date of birth cannot be in the future'],code='invalid']
					errmsg['processedon']=_('ErrorIncomingInvoiceProcessedOnFuture')
				else:
					data['processedon']=processedon

			except:
				errmsg['processedon']=_('ErrorIncomingInvoiceProcessedOnInvalid')

		else:
			errmsg['processedon']=_('ErrorIncomingInvoiceProcessedOn')


	

		try:
			provider=int(provider)
			if provider>0:
				if not Provider.objects.filter(pk=provider).exists():
					errmsg['provider']=_('ErrorIncomingInvoiceInvalidProvider')

			else:
				errmsg['provider']=_('ErrorIncomingInvoiceInvalidProvider')

		except:
			errmsg['provider']=_('ErrorIncomingInvoiceInvalidProvider')


		#if given internal reference must be unique

		if internal_reference!=None:
			internal_reference=internal_reference.strip()
			data['internal_reference']=internal_reference
			exclude={}
			if self.current_row_id>0:
				exclude['id']=self.current_row_id
			if IncomingInvoice.objects.filter(internal_reference=internal_reference).exclude(**exclude).exists():
				errmsg['internal_reference']=_('ErrorIncomingInvoiceExistingInternalReference')
		

		if provider_reference!=None:
			data['provider_reference']=provider_reference.strip()

		#items checker
		

		if self.only_invoice==0 and not items:
			errmsg['items']=_('ErrorIncomingInvoiceNoItems')

		




		if errmsg:
			raise serializers.ValidationError(errmsg)



		return data


class OutgoingInvoiceSerializer(serializers.Serializer):
	'''
	Make sure the outgoing invoice is correct.

	NO MORE IN USE. HERE FOR BACKUP ONLY. USED IN LINE WITH NewOutgoing view
	
	'''
	
	processedon=serializers.DateField()
	internal_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	items=serializers.CharField(max_length=200000,allow_blank=True,required=False)
	note=serializers.CharField(max_length=3000,required=False,allow_blank=True,allow_null=True)
	give_to=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35) #general receipent id. Its reference is based on receipent type below
	give_to_type=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)


	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(OutgoingInvoiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		processedon=data.get('processedon','')
		internal_reference=data.get('internal_reference','')
		items=data.get('items','').strip()
		give_to=data.get('give_to','').strip()
		give_to_type=data.get('give_to_type','').strip().capitalize()
		

		errmsg={}
		#we start with give to type, which determines what we will check
		ALLOWED_RECEIPENT_TYPES=[x[0] for x in settings.RECEIPENT_TYPES]

		if give_to_type not in ALLOWED_RECEIPENT_TYPES:
			errmsg['give_to_type']=_('ErrorOutgoingUnknownReceipentType')

		else:
			#the receipent is ok. So get give_to type here
			receipent_do_check=False
			try:
				give_to=int(give_to)
				if give_to<=0:
					errmsg['give_to']=_('ErrorOutgoingInvalidRecepient')
				else:
					receipent_do_check=True
					
			except:
				errmsg['give_to']=_('ErrorOutgoingInvalidRecepient')

			#should we confirm the data of the receipent here?
			if receipent_do_check:
				hr_check_msg=HRStructureCheck(give_to_type,give_to,check_active=1)
				if hr_check_msg:
					errmsg['give_to']=hr_check_msg
				

		if processedon:


				
			#convert processedon to date.
			try:
				processedon=parser.parse(str(processedon)).date()
				
				if processedon > date.today():
					
					#raise forms.ValidationError(_('Invalid birth date - date of birth cannot be in the future'],code='invalid']
					errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnFuture')

			except:
				errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')

		else:
			errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')


		#if given internal reference must be unique

		if internal_reference!=None:
			internal_reference=internal_reference.strip()
			data['internal_reference']=internal_reference
			exclude={}
			if self.current_row_id>0:
				exclude['id']=self.current_row_id
			if OutgoingInvoice.objects.filter(internal_reference=internal_reference,direction='Direct').exclude(**exclude).exists():
				errmsg['internal_reference']=_('ErrorOutgoingInvoiceExistingInternalReference')

		#check items to be given now.. Since, it can be database-costly, carry out hte check below if nothing is errorful above:
		if not errmsg:
			items=json.loads(items)
			

			if not items:
				errmsg['items']=_('ErrorOutgoingInvoiceNoItems')
			else:
				#check each.
				errors=[]
				for item in items:
					#get info
					item_details=item #dictionary
					instore_id=item_details['iteminstoreid']
					try:
						quantity=float(item_details['quantity']) #quantity asked
					except:
						quantity=0

					try:
						instore_info=ItemInStore.objects.values('store__name','store__service' , 'quantity','current_status','item__product__kind','item__product__name','item__product__active','item__product__category__active','item__product__category__name').get(pk=instore_id)
						#item exists ok. But can it be given?
						item_name=' '.join([instore_info['item__product__category__name'], instore_info['item__product__name']])
						current_quantity=float(instore_info['quantity'])
						current_status=instore_info['current_status']
						product_kind=instore_info['item__product__kind']
						store_name=instore_info['store__name']
						store_kind=instore_info['store__service']

						if current_quantity<=0:
							errors.push(_('ErrorOutgoingCurrentQuantityUndetermined') % {'item_name': item_name})
						else:
							if store_kind=='Reserve':
								errors.push(_('ErrorOutgoingProtectedStore') % {'item_name': item_name,'store':store_name})
							else:

								if quantity<=0:
									errors.push(_('ErrorOutgoingQuantityBad') % {'item_name': item_name})
								else:
									if product_kind=='Non-consumable':
										if quantity!=1:
											errors.push(_('ErrorOutgoingNonConsumableHigherThanOne') % {'item_name': item_name})
									else:
										if quantity>current_quantity:
											errors.push(_('ErrorOutgoingConsumableHigherThanInStore') % {'item_name': item_name, 'instore': str(current_quantity), 'demanded': str(quantity)})




					except:
						errors.append(_('ErrorOutgoingItemNotFound'))

				if errors:
					errmsg['items']=errors
		




		if errmsg:
			raise serializers.ValidationError(errmsg)



		return data

class ProcessRequestSerializer(serializers.Serializer):
	'''
	Make sure the outgoing invoice is correct.

	
	
	'''
	
	processedon=serializers.DateField()
	internal_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	items=serializers.CharField(max_length=200000,allow_blank=True,required=False)
	note=serializers.CharField(max_length=3000,required=False,allow_blank=True,allow_null=True)
	requested_invoice=serializers.IntegerField(required=True) #general receipent id. Its reference is based on receipent type below
	


	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ProcessRequestSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		processedon=data.get('processedon','')
		internal_reference=data.get('internal_reference','')
		items=data.get('items','').strip()
		requested_invoice=data.get('requested_invoice',0)
		
		

		errmsg={}

		try:
			invoice=RequestInvoice.objects.get(pk=requested_invoice)
			if invoice.confirmed==1:
				errmsg['requested_invoice']=_('ErrorStockOutAlreadyProcessedRequest')

			else:
				if processedon:


						
					#convert processedon to date.
					try:
						processedon=parser.parse(str(processedon)).date()
						
						if processedon > date.today():
							
							#raise forms.ValidationError(_('Invalid birth date - date of birth cannot be in the future'],code='invalid']
							errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnFuture')

					except:
						errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')

				else:
					errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')

				#if given internal reference must be unique

				if internal_reference!=None:
					internal_reference=internal_reference.strip()
					data['internal_reference']=internal_reference
					exclude={}
					if self.current_row_id>0:
						exclude['id']=self.current_row_id
					if OutgoingInvoice.objects.filter(internal_reference=internal_reference,direction='Direct').exclude(**exclude).exists():
						errmsg['internal_reference']=_('ErrorOutgoingInvoiceExistingInternalReference')

				#check items to be given now.. Since, it can be database-costly, carry out hte check below if nothing is errorful above:
				if not errmsg:
					items=json.loads(items)
					

					if not items:
						errmsg['items']=_('ErrorOutgoingInvoiceNoItems')
					else:
						#check each.
						errors=[]
						for item in items:
							#get info
							item_details=item #dictionary
							instore_id=item_details['iteminstoreid']
							try:
								quantity=float(item_details['quantity']) #quantity asked
							except:
								quantity=0

							try:
								instore_info=ItemInStore.objects.values('store__name','store__service' , 'quantity','current_status','item__product__kind','item__product__name','item__product__active','item__product__category__active','item__product__category__name').get(pk=instore_id)
								#item exists ok. But can it be given?
								item_name=' '.join([instore_info['item__product__category__name'], instore_info['item__product__name']])
								current_quantity=float(instore_info['quantity'])
								current_status=instore_info['current_status']
								product_kind=instore_info['item__product__kind']
								store_name=instore_info['store__name']
								store_kind=instore_info['store__service']

								if current_quantity<=0:
									errors.push(_('ErrorOutgoingCurrentQuantityUndetermined') % {'item_name': item_name})
								else:
									if store_kind=='Reserve':
										errors.push(_('ErrorOutgoingProtectedStore') % {'item_name': item_name,'store':store_name})
									else:

										if quantity<=0:
											errors.push(_('ErrorOutgoingQuantityBad') % {'item_name': item_name})
										else:
											if product_kind=='Non-consumable':
												if quantity!=1:
													errors.push(_('ErrorOutgoingNonConsumableHigherThanOne') % {'item_name': item_name})
											else:
												if quantity>current_quantity:
													errors.push(_('ErrorOutgoingConsumableHigherThanInStore') % {'item_name': item_name, 'instore': str(current_quantity), 'demanded': str(quantity)})




							except:
								errors.append(_('ErrorOutgoingItemNotFound'))

						if errors:
							errmsg['items']=errors
				

		except:
			errmsg['requested_invoice']=_('ErrorRequestsFormMissing')
	


		if errmsg:
			raise serializers.ValidationError(errmsg)

		else:
			data['request_data']=invoice



		return data


class ReturnInvoiceSerializer(serializers.Serializer):
	'''
	Make sure the outgoing invoice is correct
	
	'''
	
	processedon=serializers.DateField()
	internal_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	items=serializers.CharField(max_length=200000,allow_blank=True,required=False)
	note=serializers.CharField(max_length=3000,required=False,allow_blank=True,allow_null=True)
	return_by=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)
	store=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)
	
	return_by_type=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)

	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ReturnInvoiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		processedon=data.get('processedon','')
		internal_reference=data.get('internal_reference','')
		items=data.get('items','').strip()
		return_by=data.get('return_by','').strip()
		return_by_type=data.get('return_by_type','').strip()
		store=data.get('store','').strip()
		

		errmsg={}

		ALLOWED_RECEIPENT_TYPES=[x[0] for x in settings.RECEIPENT_TYPES]

		if return_by_type not in ALLOWED_RECEIPENT_TYPES:
			errmsg['give_to_type']=_('ErrorReturnUnknownReceipentType')
		else:
			returner_do_check=False
			try:
				return_by=int(return_by)
				if return_by<=0:
					errmsg['return_by']=_('ErrorReturnUnknownReceipentType')
				else:
					returner_do_check=True
					
			except:
				errmsg['return_by']=_('ErrorReturnUnknownReceipentType')

			#should we confirm the data of the entity returning the stuff here? All we care about his existence here.
			if returner_do_check:
				

				hr_check_msg=HRStructureCheck(return_by_type,return_by,check_active='No')
				if hr_check_msg:
					errmsg['return_by']=hr_check_msg


		if processedon:


				
			#convert processedon to date.
			try:
				processedon=parser.parse(str(processedon)).date()
				
				if processedon > date.today():
					
					#raise forms.ValidationError(_('Invalid birth date - date of birth cannot be in the future'],code='invalid']
					errmsg['processedon']=_('ErrorReturnItemInvoiceProcessedOnFuture')

			except:
				errmsg['processedon']=_('ErrorReturnInvoiceProcessedOnInvalid')

		else:
			errmsg['processedon']=_('ErrorReturnInvoiceProcessedOnInvalid')


		#if given internal reference must be unique

		if internal_reference!=None:
			internal_reference=internal_reference.strip()
			data['internal_reference']=internal_reference
			exclude={}
			if self.current_row_id>0:
				exclude['id']=self.current_row_id
			if ReturnItemInvoice.objects.filter(internal_reference=internal_reference).exclude(**exclude).exists():
				errmsg['internal_reference']=_('ErrorReturnInvoiceExistingInternalReference')

		if not items:
			errmsg['items']=_('ErroReturnInvoiceNoItems')

		try:
			store=int(store)
			if store>0:
				if not Store.objects.filter(pk=store,active=1).exists():
					errmsg['store']=_('ErrorReturnInvalidStore')

			else:
				errmsg['store']=_('ErrorReturnInvalidStore')

		except:
			errmsg['store']=_('ErrorReturnInvalidStore')

		


		if errmsg:
			raise serializers.ValidationError(errmsg)



		return data




class TransferInvoiceSerializer(serializers.Serializer):
	'''
	Make sure the transfer invoice is correct. Note transferes are still giving items except they are from emp to emp, instead of store to emp.
	Hence we still use OUtgoing model
	
	'''
	
	processedon=serializers.DateField()
	internal_reference=serializers.CharField(max_length=35,allow_blank=True,allow_null=True,required=False)
	items=serializers.CharField(max_length=200000,allow_blank=True,required=False)
	note=serializers.CharField(max_length=3000,required=False,allow_blank=True,allow_null=True)
	#given_from=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35) #
	#given_to=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35) #
	transfered_from=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35) #general receipent id. Its reference is based on receipent type below
	transfered_from_type=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)

	transfered_to=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)
	transfered_to_type=serializers.CharField(allow_blank=False,allow_null=False,required=True,max_length=35)

	def __init__(self,*args,**kwargs):
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(TransferInvoiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		processedon=data.get('processedon','')
		internal_reference=data.get('internal_reference','')
		items=data.get('items','').strip()

		transfered_from=data.get('transfered_from','').strip()
		transfered_from_type=data.get('transfered_from_type','').strip()

		transfered_to=data.get('transfered_to','').strip()
		transfered_to_type=data.get('transfered_to_type','').strip()
		

		errmsg={}

		ALLOWED_RECEIPENT_TYPES=[x[0] for x in settings.RECEIPENT_TYPES]



		if transfered_from_type not in ALLOWED_RECEIPENT_TYPES or transfered_to_type not in ALLOWED_RECEIPENT_TYPES:
			errmsg['transfered_from']=_('ErrorTransferUnknownEntity')

		else:
			transfer_do_check=False
			try:
				transfered_from=int(transfered_from)
				transfered_to=int(transfered_to)

				if transfered_from<=0 or transfered_to<=0:
					errmsg['transfered_from']=_('ErrorTransferUnknownEntity')
				else:
					transfer_do_check=True					
			except:
				errmsg['transfered_from']=_('ErrorTransferUnknownEntity')


			if transfer_do_check:
				#check both now. First, the source: who is giving the items? We don't care about status here.
				from_ok=True
				hr_from_check_msg=HRStructureCheck(transfered_from_type,transfered_from,check_active='No')
				if hr_from_check_msg:
					errmsg['transfered_from']=hr_from_check_msg
					from_ok=False

				to_ok=True
				hr_to_check_msg=HRStructureCheck(transfered_to_type,transfered_to,check_active=1)
				if hr_to_check_msg:
					errmsg['transfered_to']=hr_to_check_msg
					to_ok=False

				#if both are correct/valid, ensure they are not the same?

				if to_ok and from_ok:
					if transfered_from_type==transfered_to_type and transfered_from==transfered_to:
						errmsg['transfered_from']=_('ErrorTransferSameEntities')



		if processedon:


				
			#convert processedon to date.
			try:
				processedon=parser.parse(str(processedon)).date()
				
				if processedon > date.today():
					
					#raise forms.ValidationError(_('Invalid birth date - date of birth cannot be in the future'],code='invalid']
					errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnFuture')

			except:
				errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')

		else:
			errmsg['processedon']=_('ErrorOutgoingInvoiceProcessedOnInvalid')



		#if given internal reference must be unique

		if internal_reference!=None:
			internal_reference=internal_reference.strip()
			data['internal_reference']=internal_reference
			exclude={}
			if self.current_row_id>0:
				exclude['id']=self.current_row_id
			if OutgoingInvoice.objects.filter(internal_reference=internal_reference,direction='Transfer').exclude(**exclude).exists():
				errmsg['internal_reference']=_('ErrorOutgoingInvoiceExistingInternalReference')


		if not items:
			errmsg['items']=_('ErrorTransferInvoiceNoItems')

	

		if errmsg:
			raise serializers.ValidationError(errmsg)



		return data