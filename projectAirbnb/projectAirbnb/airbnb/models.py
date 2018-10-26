from django.db import models


class BnbModel(models.Model):
    class Meta:
        abstract=True
    def __init__(self,*args, **kwargs):
        super(BnbModel, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(BnbModel, self).save(*args, **kwargs)

class BnBLookupModel(BnbModel):
    class Meta:
        abstract=True
    def __init__(self,*args, **kwargs):
        super(BnBLookupModel, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(BnBLookupModel, self).save(*args, **kwargs)


class BnbDataModel(BnbModel):
    class Meta:
        abstract=True
    def __init__(self,*args, **kwargs):
        super(BnbDataModel, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(BnbDataModel, self).save(*args, **kwargs)
    
class BnbHost(BnBLookupModel):
    host_id = models.IntegerField(primary_key=True)
    host_name = models.CharField(max_length=200)
    host_since = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    host_url = models.URLField(max_length=2000, null=True, blank=True)
    host_location = models.CharField(max_length=2000, null=True, blank=True)
    about_host = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table='airbnb_host'
        verbose_name='Airbnb Host'
        verbose_name_plural='Airbnb Hosts'
    
class BnbListing(BnbDataModel):
    listing_id = models.IntegerField(primary_key=True)
    host_id = models.ForeignKey(BnbHost, to_field='host_id',db_column='host_id')
    listing_url = models.URLField(max_length=2000, null=True, blank=True)
    listing_name = models.CharField(max_length=2000, null=True, blank=True)
    listing_summary = models.TextField(null=True, blank=True)
    listing_space = models.TextField(null=True, blank=True)
    listing_description = models.TextField(null=True, blank=True)
    listing_house_rule = models.TextField(null=True, blank=True)
    picture_url = models.URLField(max_length=2000, null=True, blank=True)
    neighbourhood = models.CharField(max_length=2000, null=True, blank=True)
    city = models.CharField(max_length=2000, null=True, blank=True)
    state = models.CharField(max_length=2000, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    max_accomodation = models.CharField(max_length=100, null=True, blank=True)
    json_amenities = models.TextField(null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    number_of_reviews=models.CharField(max_length=100, null=True, blank=True)
    review_per_month = models.CharField(max_length=100, null=True, blank=True)
    review_scores_rating = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table='airbnb_listing'
        verbose_name='Airbnb Listing'
        verbose_name_plural='Airbnb Listings'

    
class BnbReview(BnbDataModel):
    review_id = models.IntegerField(primary_key=True)
    listing_id = models.ForeignKey(BnbListing, to_field='listing_id',db_column='listing_id')
    review_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    reviewer_name = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    class Meta:
        db_table='airbnb_listing_review'
        verbose_name='Airbnb Listing Review'
        verbose_name_plural='AAirbnb Listing Reviews'
#listFiles=[r'C:\Users\schan\Desktop\PGPBA\Class3\data_host.csv', r'C:\Users\schan\Desktop\PGPBA\Class3\data_listing.csv', 