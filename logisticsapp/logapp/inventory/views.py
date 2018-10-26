
from tools.formtools import createErrorDataJSON

from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse



from inventory.models import Category,CategoryRevision,Product,ProductRevision,Brand,BrandRevision,Manufacturer,ManufacturerRevision,Store,StoreRevision

from logistic.models import IncomingItem,ItemInStore,OutgoingItem,ReturnItem,RequestedItem


from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo


from inventory.serializers import BrandSerializer, CategorySerializer, ProductSerializer, StoreSerializer

import os
import json
from tools.revisions import addRecordRevision
from tools.publish import publishCatalogStructureJSON
from app.conf import base as settings


class CategoriesList(APIView):
	'''
	This module display list of Categories. The role is limited to ALL but pass can_manage for front-end to play with
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=200
		have_right=userIsPermittedTo(request.user.id,['add_category'])
		reply['can_manage']=have_right
		filters={}

		if have_right==False:
			#show only active heads
			filters['active']=1


		reply['detail']=list(Category.objects.filter(**filters).values('id','name','asset_code','active').order_by('name',))
		status=200			


		return JsonResponse(reply,status=status)


class CategoryAdd(APIView):
	'''
	Add a new category. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_category'])

		if have_right:
			#process
			data=request.data
			serializer=CategorySerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Category(name=content['name'],active=content['active'], added_by_id=request.user.id,asset_code=content['asset_code'])
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('InventoryCategoryAddOk')
					status=200
					publishCatalogStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorInventoryCategoryAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)

class CategoryInformation(APIView):
	'''
	View Category information. NOte this is exactly the same as edit below but kept cos the API's could be confusing plus the powers differ
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_catalog'])

		if have_right:
			#get the category
			try:
				reply['detail']=Category.objects.values('id','name','asset_code','active').get(pk=record_id)
				status=200
			except:
				reply['detail']=_('ErrorInventoryCategoryNotFound')
			

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)

class CategoryEdit(APIView):
	'''
	Edit an existing Brand. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_category'])

		if have_right:
			#get the category
			try:
				reply['detail']=Category.objects.values('id','name','asset_code','active').get(pk=record_id)
				status=200
			except:
				reply['detail']=_('ErrorInventoryCategoryNotFound')
			

		else:
			reply['detail']=_('NoRight')




		return JsonResponse(reply,status=status)



	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_category'])

		if have_right:
			#process
			data=request.data
			serializer=CategorySerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					category=Category.objects.get(pk=record_id)
					current_name=category.name
					category.name=content['name']
					category.active=content['active']
					category.asset_code=content['asset_code']
					category.save()
					status=200
					publishCatalogStructureJSON(user_id=request.user.id)
					reply['detail']=_('InventoryCategoryUpdateOk')
					addRecordRevision(CategoryRevision, record_id, current_name, content['name'], request.user.id, _('InventoryCategory'))
				except:
					reply['detail']=_('ErrorInventoryCategoryNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class CategoryDelete(APIView):
	'''
	Delete the requested category. It must not have transactions under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_category'])

		if have_right:
			#process

			try:
				category=Category.objects.get(pk=record_id)
				#make sure there is no item
				if IncomingItem.objects.filter(product__category_id=record_id).exists():
					reply['detail']=_('ErrorInventoryDeleteItemsExists')
				else:
					#delete
					category.delete()
					status=200
					publishCatalogStructureJSON(user_id=request.user.id)
					reply['detail']=_('InventoryDeleteCategory')
			except:
				reply['detail']=_('ErrorInventoryCategoryNotFound')

			

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)






'''
* Products MANAGEMENT AND VIEWING
'''

class ProductsList(APIView):
	'''
	This module display list of products in a category. The role is limited to Manager,Logistic Officer, DAF Officer Only.
	Note that we can view all products if category_id=0 or just the products in category_id
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,category_id,format=None):
		reply={}
		status=400

		category_id=int(category_id)

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_catalog'])


		if have_right:
			#return list of products
			filters={'category_id':category_id}
			if have_right==False:
				#show only active
				filters['active']=1

			fields=['id','name','category_id','measurement_unit','kind','active','category__name','asset_code','lasts_for_years','depreciation_method','min_value','max_value']
			
		
			
			reply['detail']=list(Product.objects.filter(**filters).values(*fields).order_by('name',))
			#send back all categories -- active or inactive for easy switcing of products from current category to anoter one
			reply['categories']=list(Category.objects.all().values('id','name').order_by('name'))

			
			status=200			
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)





class ProductAdd(APIView):
	'''
	Add a new product to Category. Only Administrator can do that. We can add to an inactive Category, long as it exists.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,category_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_product'])

		if have_right:
			#process
			data=request.data
			serializer=ProductSerializer(data=data,current_id=0,category_id=category_id)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Product(depreciation_method=content['depreciation_method'],min_value=content['min_value'],max_value=content['max_value'],lasts_for_years=content['lasts_for_years'],name=content['name'],active=content['active'],category_id=category_id,added_by_id=request.user.id,kind=content['kind'],measurement_unit=content['measurement_unit'],asset_code=content['asset_code'])
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('InventoryProductAddOk')
					status=200
					publishCatalogStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorInventoryProductAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class ProductEdit(APIView):
	'''
	Edit an existing Product. Only Administrator can do that.
	
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,category_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_product'])

		if have_right:
			#process
			try:
				reply['product']=Product.objects.values('id','name','kind','measurement_unit','asset_code','active','category_id','depreciation_method','lasts_for_years','min_value','max_value').get(pk=record_id,category_id=category_id)
				reply['categories']=list(Category.objects.all().values('id','name').order_by('name',))
				status=200
			except:
				reply['detail']=_('ErrorInventoryProductNotFound')


		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


	def post(self,request,category_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_product'])

		if have_right:
			#process
			data=request.data
			serializer=ProductSerializer(data=data,current_id=record_id,category_id=category_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					product=Product.objects.get(pk=record_id)
					current_name=product.name
					product.name=content['name']
					product.active=content['active']
					product.depreciation_method=content['depreciation_method']
					product.lasts_for_years=content['lasts_for_years']
					product.category_id=category_id
					product.asset_code=content['asset_code']
					product.measurement_unit=content['measurement_unit']
					
					product.kind=content['kind']
					product.min_value=content['min_value']
					product.max_value=content['max_value']
					product.save()
					publishCatalogStructureJSON(user_id=request.user.id)
					status=200
					reply['detail']=_('InventoryProductUpdateOk')
					addRecordRevision(ProductRevision, record_id, current_name, content['name'], request.user.id, _('InventoryProduct'))
				except:
					reply['detail']=_('ErrorInventoryProductNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class ProductDelete(APIView):
	'''
	Delete the requested product. For product to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,category_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_product'])

		if have_right:
			#process

			try:
				product=Product.objects.get(pk=record_id,category_id=category_id)
				#delete here
				if IncomingItem.objects.filter(product_id=record_id).exists():
					reply['detail']=_('ErrorInventoryDeleteItemsExists')
				else:
					product.delete()
					status=200
					publishCatalogStructureJSON(user_id=request.user.id)
					reply['detail']=_('InventoryProductDeleteOk')
			except:
				reply['detail']=_('ErrorInventoryProductNotFound')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class MergeCategory(APIView):
	'''
	Moves products in one category into another and optionally deletes the category
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400
		if userIsPermittedTo(request.user.id,['can_merge_categories']):
			source_cat=request.data.get('source','')
			dest_cat=request.data.get('dest','')
			delete_after=request.data.get('delete_after','').strip().lower()

			err_msg={}

			try:
				source=Category.objects.get(pk=source_cat)
			except:
				err_msg['source']=_('ErrorMergeCategorySourceMissing')

			try:
				dest=Category.objects.get(pk=dest_cat)
			except:
				err_msg['dest']=_('ErrorMergeCategoryDestMissing')

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)


			else:
				if source.id==dest.id:
					reply['detail']=_('ErrorMergeCategorySame')
				else:

					#indeed move
					status=200
					products=Product.objects.filter(category_id=source_cat).update(category_id=dest_cat)
					#do we need to delete te source category now?
					reply['detail']=_('MergedCategory') % {'source':source.name,'dest':dest.name}
					if delete_after=='y':
						source.delete()

					publishCatalogStructureJSON(user_id=request.user.id)
					catalog_file=os.path.join(settings.BASE_DIR,'static/public/items.json')
					with open(catalog_file) as data:
						try:
							json_data=json.load(data)
						except:
							json_data=[]
					reply['catalog']=json_data




		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class MoveProductsToCategory(APIView):
	'''
	We move products from one category to another

	@Input: CSV list of products
	@Input: the new category
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		if userIsPermittedTo(request.user.id,['can_move_products_to_categories']):
			dest_cat=request.data.get('dest','')
			products=request.data.get('products') #csv

			err_msg={}

			try:
				dest=Category.objects.get(pk=dest_cat)
			except:
				err_msg['dest']=_('ErrorMergeCategoryDestMissing')

			#products=csvFromUrlToNumbers(products)
			if not products:
				err_msg['products']=_('ErrorMoveProductsNoProducts')

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)

			else:
				target_products=Product.objects.filter(pk__in=products).update(category_id=dest_cat)
				status=200
				reply['detail']=_('ProductsMovedToCategory') % {'cat':dest.name}
				publishCatalogStructureJSON(user_id=request.user.id)
				catalog_file=os.path.join(settings.BASE_DIR,'static/public/items.json')
				with open(catalog_file) as data:
					try:
						json_data=json.load(data)
					except:
						json_data=[]
				reply['catalog']=json_data


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class MergeProducts(APIView):
	'''
	Moves items in checked products to the selected products then deletes those products optionalletes it
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400
		if userIsPermittedTo(request.user.id,['can_merge_products']):
			products=request.data.get('products','')
			dest_pro=request.data.get('dest','')
			delete_after=request.data.get('delete_after','').strip().lower()

			err_msg={}


			try:
				dest=Product.objects.get(pk=dest_pro)
			except:
				err_msg['dest']=_('ErrorMergeProductDestMissing')

			if not products:
				err_msg['products']=_('ErrorMoveProductsNoProducts')

			if err_msg:
				reply['detail']=createErrorDataJSON(err_msg,2)


			else:
				

				#indeed move
				registered_items=IncomingItem.objects.filter(product_id__in=products).exclude(product_id=dest_pro).update(product_id=dest_pro)
				requested_items=RequestedItem.objects.filter(product_id__in=products).exclude(product_id=dest_pro).update(product_id=dest_pro)
				status=200
				
				#do we need to delete te old product now?
				reply['detail']=_('MergedProducts') % {'dest':dest.name}
				if delete_after=='y':
					products=Product.objects.filter(pk__in=products).exclude(pk=dest_pro)

					reply['sql']=str(products.query)

					products.delete()

				publishCatalogStructureJSON(user_id=request.user.id)
				catalog_file=os.path.join(settings.BASE_DIR,'static/public/items.json')
				with open(catalog_file) as data:
					try:
						json_data=json.load(data)
					except:
						json_data=[]
				reply['catalog']=json_data
					
					



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)












#------------------------------------------------------------------------------

class BrandsList(APIView):
	'''
	This module display list of Brands. The role is limited to ALL.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		reply['can_manage']=userIsPermittedTo(request.user.id,['add_brand','change_brand','delete_brand'])

		reply['detail']=list(Brand.objects.all().values('id','name','is_unknown').order_by('name',))
		
		status=200			
		

		return JsonResponse(reply,status=status)


class BrandAdd(APIView):
	'''
	Add a new brand. Only Logistics Officer can do that.

	If a brand exists already, simply don't add it.

	Note we declare a particular product as unknown from the specific admin management tool only (power of the admin)

	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_brand'])

		if have_right:
			#process
			data=request.data
			#does the name exist?

			serializer=BrandSerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				#see if name exists
				name=content['name']
				new_id=0

				try:
					brand=Brand.objects.get(name=name)
					new_id=brand.id
				except:
					#add it here
					add_new=Brand(name=name,is_unknown=0,note=content['note'],added_by_id=request.user.id)
					add_new.save()
					if add_new:
						new_id=add_new.id

				if new_id>0:
					reply['new_id']=new_id
					reply['detail']=_('InventoryBrandAddedSuccessfully')
					status=200
				else:
					reply['detail']=_('ErrorInventoryBrandAddError')


			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class BrandEdit(APIView):
	'''
	Edit an existing Brand. Only Logisitic Officer can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]


	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_brand'])

		if have_right:
			#process
			data=request.data
			serializer=BrandSerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				

				try:
					brand=Brand.objects.get(pk=record_id)

					current_name=brand.name

					brand.name=content['name']
					
					brand.save()
					status=200
					reply['detail']=_('InventoryBrandUpdateOk')
					addRecordRevision(BrandRevision, record_id, current_name, content['name'], request.user.id, _('InventoryCategory'))
				except:
					reply['detail']=_('ErrorInventoryBrandNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class BrandDelete(APIView):
	'''
	Delete the requested brand. It must not have transactions under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_brand'])

		if have_right:
			#process

			try:
				brand=Brand.objects.get(pk=record_id)
				#delete here
				status=200
			except:
				reply['detail']=_('ErrorInventoryBrandNotFound')

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


#----------------------------------------------------------------------------------------------

class ManufacturersList(APIView):
	'''
	This module display list of Manufacturers. The role is limited to ALL.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

			
		reply['can_manage']=userIsPermittedTo(request.user.id,['add_manufacturer','change_manufacturer','delete_manufacturer'])

		reply['detail']=list(Manufacturer.objects.all().values('id','name','is_unknown').order_by('name',))
		
		status=200			
		

		return JsonResponse(reply,status=status)


class ManufacturerAdd(APIView):
	'''
	Add a new manufacturer. Only Logistics Officer can do that.

	If a manufacturer exists already, simply don't add it.

	Note we declare a particular product as unknown from the specific admin management tool only (power of the admin)

	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_manufacturer'])

		if have_right:
			#process
			data=request.data
			#does the name exist?

			serializer=BrandSerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				#see if name exists
				name=content['name']
				new_id=0

				try:
					manufacturer=Manufacturer.objects.get(name=name)
					new_id=manufacturer.id
				except:
					#add it here
					add_new=Manufacturer(name=name,is_unknown=0,note=content['note'],added_by_id=request.user.id)
					add_new.save()
					if add_new:
						new_id=add_new.id

				if new_id>0:
					reply['new_id']=new_id
					reply['detail']=_('InventoryManufactrerAddedSuccessfully')
					status=200
				else:
					reply['detail']=_('ErrorInventoryManufactrerAddError')


			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class ManufacturerEdit(APIView):
	'''
	Edit an existing Brand. Only Logisitic Officer can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]


	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_manufacturer'])

		if have_right:
			#process
			data=request.data
			serializer=BrandSerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				

				try:
					manufacturer=Manufacturer.objects.get(pk=record_id)

					current_name=manufacturer.name

					manufacturer.name=content['name']
					
					manufacturer.save()
					status=200
					reply['detail']=_('InventoryManufactrerUpdateOk')
					addRecordRevision(ManufacturerRevision, record_id, current_name, content['name'], request.user.id, _('InventoryManufacturer'))
				except:
					reply['detail']=_('ErrorInventoryManufactrerNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class ManufacturerDelete(APIView):
	'''
	Delete the requested manufacturer. It must not have transactions under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_manufacturer'])

		if have_right:
			#process

			try:
				manufacturer=Manufacturer.objects.get(pk=record_id)
				#delete here
				status=200
			except:
				reply['detail']=_('ErrorInventoryManufactrerNotFound')

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



#-----------------------------------------------------------


class StoresList(APIView):
	'''
	This module display list of Stores. The role is limited to 'Auditor','Logistic Officer','DAF Officer','Manager'
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_store','change_store','delete_store'])
		reply['can_manage']=have_right
		filters={}

		if have_right==False:
			#show only active heads
			filters['active']=1

		reply['detail']=list(Store.objects.filter(**filters).values('id','name','service','active').order_by('name',))

		
		status=200			
		

		return JsonResponse(reply,status=status)


class StoreAdd(APIView):
	'''
	Add a new store. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_store'])

		if have_right:
			#process
			data=request.data
			serializer=StoreSerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Store(name=content['name'],active=content['active'], added_by_id=request.user.id,service=content['kind'])
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('InventoryStoreAddOk')
					publishCatalogStructureJSON(user_id=request.user.id)
					status=200
				else:
					reply['detail']=_('ErrorInventoryStoreAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class StoreEdit(APIView):
	'''
	Edit an existing Store. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_store'])

		if have_right:
			#get the store
			try:
				reply['detail']=Store.objects.values('id','name','service','active').get(pk=record_id)
				status=200

			except:
				reply['detail']=_('ErrorInventoryStoreNotFound')
			

		else:
			reply['detail']=_('NoRight')




		return JsonResponse(reply,status=status)



	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_store'])

		if have_right:
			#process
			data=request.data
			serializer=StoreSerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					store=Store.objects.get(pk=record_id)
					current_name=store.name
					store.name=content['name']
					store.active=content['active']
					store.service=content['kind']
					store.save()
					publishCatalogStructureJSON(user_id=request.user.id)
					status=200
					reply['detail']=_('InventoryStoreUpdateOk')
					addRecordRevision(StoreRevision, record_id, current_name, content['name'], request.user.id, _('InventoryStore'))
				except:
					reply['detail']=_('ErrorInventoryStoreNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class StoreDelete(APIView):
	'''
	Delete the requested store. It must not have transactions under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_store'])

		if have_right:
			#process

			try:
				store=Store.objects.get(pk=record_id)
				#delete here. Check out its history here?
				#ItemInStore,OutgoingItem,ReturnItem

				if ItemInStore.objects.filter(store_id=record_id).exists():
					reply['detail']=_('ErrorInventoryDeleteStoreContainsItems')
				else:
					if OutgoingItem.objects.filter(given_from_store_id=record_id).exists():
						reply['detail']=_('ErrorInventoryDeleteStoreContainsOutgoingHistory')
					else:
						if ReturnItem.objects.filter(return_to_store_id=record_id).exists():
							reply['detail']=_('ErrorInventoryDeleteStoreContainsReturnHistory')
						else:
							#delete here
							store.delete()
							reply['detail']=_('InventoryStoreDeleteOk')
							status=200
							publishCatalogStructureJSON(user_id=request.user.id)


				
			except:
				reply['detail']=_('ErrorInventoryStoreNotFound')

			

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)