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

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from app.conf import base as settings
from logistic.models import IncomingItem,TechnicalService
from datetime import date
from dateutil import parser



class TechnicalServiceSerializer(serializers.Serializer):
	'''
	Is the service information valid. Regardless of editing or adding new, the CURRENT ITEM STATUS MUST NOT BE LOST.
	'''
	action=serializers.CharField(max_length=8,allow_blank=False,required=True)
	arrivedon=serializers.DateField()
	comment=serializers.CharField(max_length=2000,required=False,allow_blank=True,allow_null=True)
	monetary_value=serializers.DecimalField(max_digits=19, decimal_places=10,default=0)
	manpower_value=serializers.DecimalField(max_digits=19, decimal_places=10,default=0)
	new_status=serializers.CharField(max_length=30,default=None)

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.item_tag=kwargs.pop('item_tag','')
		super(TechnicalServiceSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		errmsg={}
		item_id=0
		try:
			item=IncomingItem.objects.get(tag=self.item_tag,product__kind='Non-consumable')
			if item.current_status=='LOST':
				errmsg['item']=_('ErrorServiceItemIsLost')
			else:
				#to avoid quering again. Send the item data back to the caller to be used during adding or editing an information
				data['item_id']=item.id
				item_id=item.id

		except:
			errmsg['item']=_('ErrorItemNotFound')

		if self.current_row_id>0:
			#editing an existing service information. Make sure it exists and it is for the tagged or passed item above
			if not TechnicalService.objects.filter(pk=self.current_row_id,item_id=item_id):
				errmsg['service']=_('ErrorServiceEditNotFound')

		action=data.get('action','').strip().capitalize()

		allowed_actions=[x[0] for x in TechnicalService.ACTION]

		if action not in allowed_actions:
			errmsg['action']=_('ErrorServiceInvalidAction')


		arrivedon=data.get('arrivedon',None)

		if arrivedon:

			#convert arrivedon to date.
			try:
				arrivedon=parser.parse(str(arrivedon)).date()
				
				if arrivedon > date.today():
					
				
					errmsg['arrivedon']=_('ErrorServiceDateOnFuture')

			except:
				errmsg['arrivedon']=_('ErrorServiceDateInvalid')

		else:
			errmsg['arrivedon']=_('ErrorServiceDate')

		monetary_value=data.get('monetary_value',0)

		try:
			monetary_value=float(monetary_value)
			if monetary_value<0:
				errmsg['monetary_value']=_('ErrorServiceMonetaryValueInvalid')

		except:
			errmsg['monetary_value']=_('ErrorServiceMonetaryValueInvalid')


		manpower_value=data.get('manpower_value',0)
		try:
			manpower_value=float(manpower_value)
			if manpower_value<0:
				errmsg['manpower_value']=('rrorServiceManPowerValueInvalid')
		except:
			errmsg['manpower_value']=_('rrorServiceManPowerValueInvalid')

		new_status=data.get('new_status','').strip().capitalize()
		#it must be valid inside an allowed status but NOT LOST/UNKNOWN/NOT APPLICABLE
		STATUS=[x[0] for x in settings.STATUS]
		#STATUS=(('Unknown',_('Unknown')), ('Burned',_('Burned')) ,('New',_('New')), ('Used',_('Used')), ('Defective',_('Defective')), ('Disfunctional',_('Disfunctional')), ('Not Applicable',('NotApplicable')),('Lost',_('Lost')))
		#purify allowed status now. Note faster to create a new list than to modify it. Refer to Python 3.6 Documentation
		STATUS= [e for e in STATUS if e not in ('Lost','Unknown','Not Applicable')]

		if new_status.lower()!='unchanged':
			if new_status not in STATUS:
				errmsg['new_status']=_('ErrorServiceStatusInvalid') % {'allowed_status':','.join(STATUS)}
		else:
			data['new_status']='Unchanged' #this ensures that the current status of the item in history/store wont be affected.


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data




