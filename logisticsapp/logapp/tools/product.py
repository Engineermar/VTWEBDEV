from inventory.models import Product,Brand,Manufacturer

def logisticProductInformation(id):
	'''
	Return product info of a specific product. Note this is not a speficic laptop for e.g. But all "Laptop" found in Product moodel

	@input: id of the product
	'''
	reply={}
	try:
		reply=Product.objects.values('active','category__asset_code','asset_code','name','category__name','kind','lasts_for_years').get(pk=id)
	except:
		reply={}

	return reply



def registerNewProductBrand(name,user_id):
	'''
	Each product is expected to have a brand but it might not have. We register brands here.

	@input name: name of the brand (e.g. Thinkpad T520)
	@input user_id: the user who is registering the brand

	If a brand exists with the same name, return the id of the existing brand. Else,register it

	@output: id of the exsting brand with same name or the newly registered brand
	
	'''
	id=0
	try:
		brand=Brand.objects.get(name=name)
		id=brand.id
	except:
		brand=Brand(name=name,added_by_id=user_id)
		brand.save()
		if brand:
			id=brand.id
	return id

def registerNewProductManafacturer(name,user_id):
	'''
	Each product is expected to have a manf but it might not have. We register manfacutererss here.

	@input name: name of the manf (e.g. Lenovo)
	@input user_id: the user who is registering the manf

	If a manf exists with the same name, return the id of the existing manf. Else,register it

	@output: id of the exsting manf with same name or the newly registered manf
	
	'''
	id=0
	try:
		manf=Manufacturer.objects.get(name=name)
		id=manf.id
	except:
		manf=Manufacturer(name=name,added_by_id=user_id)
		manf.save()
		if manf:
			id=manf.id
	return id

