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
from inventory.models import Category,Product,Brand,Manufacturer,Store
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from validation.validators import validateCharacters
import app.appsettings as appsettings


class CategorySerializer(serializers.Serializer):
	'''
	Make sure Category information is ok before you save it
	'''
	name=serializers.CharField(max_length=80,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	asset_code=serializers.CharField(max_length=12,required=False,allow_blank=True,allow_null=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(CategorySerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		asset_code=data.get('asset_code','')

		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorInventoryCategoryNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now
				ensure_unique={}
				if self.current_row_id>0:
					ensure_unique['id']=self.current_row_id

				if Category.objects.filter(name=name).exclude(**ensure_unique).exists():
					errmsg['name']=_('ErrorInventoryCategoryNameExists')



		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')

		#confirm asset code. If given, it gotta be unique

		if asset_code:
			asset_code=asset_code.strip()
			check_invalid_characters=validateCharacters(asset_code, _('Name'))
			if check_invalid_characters:
				errmsg['asset_code']=check_invalid_characters
			else:
				ensure_unique={}
				if self.current_row_id>0:
					ensure_unique['id']=self.current_row_id


				if Category.objects.filter(asset_code=asset_code).exclude(**ensure_unique).exists():
					errmsg['asset_code']=_('ErrorInventoryCategoryAssetCodeExists')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data



class ProductSerializer(serializers.Serializer):
	'''
	Make sure Product information is ok before you save it
	'''
	name=serializers.CharField(max_length=80,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	kind=serializers.CharField(max_length=300,allow_blank=False,required=True)
	measurement_unit=serializers.CharField(max_length=5,allow_blank=False,required=True)
	asset_code=serializers.CharField(max_length=12,allow_blank=True,required=False,allow_null=True)
	depreciation_method=serializers.CharField(max_length=20,allow_blank=True,required=False)
	lasts_for_years=serializers.IntegerField()
	min_value=serializers.DecimalField(max_digits=15,decimal_places=2,default=0)
	max_value=serializers.DecimalField(max_digits=15,decimal_places=2,default=0)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.category_id=int(kwargs.pop('category_id',0))
		super(ProductSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		kind=data.get('kind','').strip().capitalize()
		measure=data.get('measurement_unit').strip().capitalize()
		asset_code=data.get('asset_code','')
		depreciation_method=data.get('depreciation_method','').strip()
		lasts_for_years=data.get('lasts_for_years',0)
		min_value=data.get('min_value',0)
		max_value=data.get('max_value',0)
		
		DEPRECIATION_METHODS=[x[0] for x in Product.DEPRECIATION_METHODS]
		KINDS=[x[0] for x in Product.KIND]


		
		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorInventoryProductNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now. Make sure the head exists first
				#if given asset code should be unique too:
				if asset_code:
					ensure_unique={}
					if self.current_row_id>0:
						ensure_unique['id']=self.current_row_id
					if Product.objects.filter(asset_code=asset_code).exclude(**ensure_unique).exists():
						errmsg['asset_code']=_('ErrorInventoryAssetCodeExists')

				if self.category_id<=0:
					errmsg['category']=_('ErrorInventoryProductInvalidCategory')
				else:
					try:
						category=Category.objects.get(pk=self.category_id)
						#head is ok. Ensure the name of the department is unique within the Head now
						ensure_unique={}
						
						if self.current_row_id>0:
							ensure_unique['id']=self.current_row_id
							ensure_unique['category_id']=self.category_id

						if Product.objects.filter(name=name,category_id=self.category_id).exclude(**ensure_unique).exists():
							errmsg['name']=_('ErrorInventoryCategoryNameExists') % {'cat_name':category.name,'product_name':name}

					except:
						errmsg['category']=_('ErrorInventoryProductInvalidCategory')

		if not measure:
			errmsg['measurement_unit']=_('ErrorInventoryProductInvalidMeasurement')

		if kind not in KINDS:
			errmsg['kind']=_('ErrorInventoryProductInvalidKind')
		else:
			if kind=='Non-consumable':
				#check depreciation
				if depreciation_method not in DEPRECIATION_METHODS:
					errmsg['depreciation_method']=_('ErrorInventoryDepreciationeMethodInvalid')
				else:
					if depreciation_method=='NA':
						errmsg['depreciation_method']=_('ErrorInventoryDepreciationeMethodInvalid')


				try:
					lasts_for_years=int(lasts_for_years)
					if lasts_for_years<0:
						errmsg['lasts_for_years']=_('ErrorInventoryDepreciationeLifeTimeInvalid')

				except:
					errmsg['lasts_for_years']=_('ErrorInventoryDepreciationeLifeTimeInvalid')

				

			else:
				data['lasts_for_years']=0
				data['depreciation_method']='NA'
				


		if min_value<0:
			errmsg['min_value']=_('ErrorInventoryMinValueIsZero')
		else:
			if min_value>max_value:
				errmsg['min_value']=_('ErrorInventoryMinValueIsLarger')


				


		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data



class BrandSerializer(serializers.Serializer):
	'''
	Make sure Brand information is ok before you save it. Note that Brand name can be repeated and we don't treat as errors. But
	'''
	name=serializers.CharField(max_length=80,allow_blank=False,required=True)
	note=serializers.CharField(max_length=3000,allow_blank=True,required=False)
	
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(BrandSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		
		note=data.get('note','').strip()
		

		errmsg={}

		if len(name)<1:
			errmsg['name']=_('ErrorInventoryBrandNameShort') % {'min': '1'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters
			else:
				if self.current_row_id>0:
					#editing. see if same brand exists
					if Brand.objects.filter(name=name).exclude(pk=self.current_row_id).exists():
						errmsg['name']=_('ErrorInventoryBrandNameExists')

		

		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data


class ManafSerializer(serializers.Serializer):
	'''
	Make sure manufacteur information is ok before you save it. Note that Brand name can be repeated and we don't treat as errors. But
	'''
	name=serializers.CharField(max_length=80,allow_blank=False,required=True)
	note=serializers.CharField(max_length=3000,allow_blank=True,required=False)
	
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ManafSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		
		note=data.get('note','').strip()
		

		errmsg={}

		if len(name)<2:
			errmsg['name']=_('ErrorInventoryManfNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters
			else:
				if self.current_row_id>0:
					#editing. see if same brand exists
					if Manufacturer.objects.filter(name=name).exclude(pk=self.current_row_id).exists():
						errmsg['name']=_('ErrorInventoryManNameExists')

		

		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data



class StoreSerializer(serializers.Serializer):
	'''
	Make sure Store information is ok before you save it
	'''
	name=serializers.CharField(max_length=30,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	kind=serializers.CharField(max_length=20,allow_blank=False,required=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(StoreSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		kind=data.get('kind','').strip().lower()

		errmsg={}

		KINDS=[x[0].lower() for x in Store.SERVICES]

		if len(name)<1:
			errmsg['name']=_('ErrorInventoryStoreNameShort') % {'min': '1'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now
				ensure_unique={}
				if self.current_row_id>0:
					ensure_unique['id']=self.current_row_id

				if Store.objects.filter(name=name).exclude(**ensure_unique).exists():
					errmsg['name']=_('ErrorInventoryStoreNameExists')



		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		

		if kind not in KINDS:
			errmsg['kind']=_('ErrorInventoryStoreInvalidKind')



		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data



