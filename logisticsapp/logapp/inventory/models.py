from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import app.appsettings as appsettings

# Create your models here.


class Category(models.Model):
	'''
	Category model refers to the top level in the hierrarchy of items. For e.g. Computing, Transportation, Apparels etc.
	Here, we don't store items directly at all.
	'''
	name=models.CharField(max_length=80,unique=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='category_user')
	asset_code=models.CharField(max_length=15,null=True,blank=True)
	active=models.PositiveIntegerField(default=1)

class CategoryRevision(models.Model):
	'''
	For changes that are made to the name of a category above, we keep track here. THis is purely for management reasons.
	The field "source" is named that way to make development easy since revisions could work for other models as well. For many, we track names only anyway.
	'''
	source=models.ForeignKey(Category,related_name='category_revision')
	user=models.ForeignKey(User,related_name='category_user_revision')
	pre_name=models.CharField(max_length=80)
	new_name=models.CharField(max_length=80)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)





class Product(models.Model):
	'''
	Product model stores products which are children of categories.For e.g. Computing category have Laptop, Printer,Desktop under it
	We add only the person who had originally added it but we keep revisions down.
	'''
	KIND=( ('Consumable',_('Consumable')), ('Non-consumable',_('NonConsumable')))
	DEPRECIATION_METHODS=(('NA','NA'),('StraightLine','StraightLine'), ('DoubleDecline','DoubleDecline'))
	name=models.CharField(max_length=80)
	category=models.ForeignKey(Category,related_name='category_product')
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='product_user')
	
	measurement_unit=models.CharField(max_length=50)
	kind=models.CharField(choices=KIND,max_length=25)
	active=models.PositiveIntegerField(default=1)
	asset_code=models.CharField(max_length=15,null=True,blank=True)
	lasts_for_years=models.PositiveIntegerField(default=0)
	depreciation_method=models.CharField(choices=DEPRECIATION_METHODS,max_length=20,default=None,null=True,blank=True)
	min_value=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	max_value=models.DecimalField(max_digits=15,decimal_places=2,default=0)
	



class ProductRevision(models.Model):
	'''
	For changes that are made to the name of a product above, we keep track here. THis is purely for management reasons.
	The field "source" is named that way to make development easy since revisions could work for other models as well. For many, we track names only anyway.
	'''
	source=models.ForeignKey(Product,related_name='product_revision')
	user=models.ForeignKey(User,related_name='product_user_revision')
	pre_name=models.CharField(max_length=80)
	new_name=models.CharField(max_length=80)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)






class Brand(models.Model):
	'''
	Brand model stores possible brand of items. Brands are attached with individual items typically. Note that it must always have an entry with Unknown it that cant be changed at all.
	Example of a brand is Optiplex 300.
	Note that we don't store manufacturer here
	Note 2: there can only be ONE is_unknown=1
	Note 3: we store only the person who created it here. note the one who added it. However, we store history of revisions.

	'''
	name=models.CharField(max_length=80,unique=True)
	is_unknown=models.PositiveIntegerField(default=0)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='brand_user')
	note=models.CharField(max_length=3000,null=True,blank=True,default=None)


class BrandRevision(models.Model):
	'''
	For changes that are made to the name of a brand above, we keep track here. THis is purely for management reasons.
	The field "source" is named that way to make development easy since revisions could work for other models as well. For many, we track names only anyway.
	'''
	source=models.ForeignKey(Brand,related_name='brand_revision')
	user=models.ForeignKey(User,related_name='brand_user_revision')
	pre_name=models.CharField(max_length=80)
	new_name=models.CharField(max_length=80)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)



class Manufacturer(models.Model):
	'''
	Manufacturer model stores possible brand of items. They are attached with individual items typically. Note that it must always have an entry with Unknown it that cant be changed at all.
	Example of a manufactuere is Dell.
	Note that we don't store brand here
	Note 2: there can only be ONE is_unknown=1
	Note 3: we store only the person who created it here. note the one who added it. However, we store history of revisions.

	'''
	name=models.CharField(max_length=80,unique=True)
	is_unknown=models.PositiveIntegerField(default=0)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='manu_user')
	note=models.CharField(max_length=3000,null=True,blank=True,default=None)


class ManufacturerRevision(models.Model):
	'''
	For changes that are made to the name of a manufacturer above, we keep track here. THis is purely for management reasons.
	The field "source" is named that way to make development easy since revisions could work for other models as well. For many, we track names only anyway.
	'''
	source=models.ForeignKey(Manufacturer,related_name='manu_revision')
	user=models.ForeignKey(User,related_name='manu_user_revision')
	pre_name=models.CharField(max_length=80)
	new_name=models.CharField(max_length=80)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)


class Store(models.Model):
	'''
	list of stores owned by Owner
	'''
	SERVICES=(('Reserve',_('StoreIn')) , ('Distribution',_('StoreInOut'))  )
	name=models.CharField(max_length=30,unique=True)
	service=models.CharField(default='Distribution',choices=SERVICES,max_length=30)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='store_user')
	active=models.PositiveIntegerField(default=1)


class StoreRevision(models.Model):
	'''
	For changes that are made to the name of a store above, we keep track here. THis is purely for management reasons.
	The field "source" is named that way to make development easy since revisions could work for other models as well. For many, we track names only anyway.
	'''
	source=models.ForeignKey(Manufacturer,related_name='store_revision')
	user=models.ForeignKey(User,related_name='store_user_revision')
	pre_name=models.CharField(max_length=30)
	new_name=models.CharField(max_length=30)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)

	
