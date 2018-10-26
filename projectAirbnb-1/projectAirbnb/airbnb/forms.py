from django.forms import ModelForm
from airbnb.models import BnbHost, BnbListing, BnbReview

# Create the form class.
class BnbHostForm(ModelForm):
    class Meta:
        model = BnbHost
        fields = ['host_name', 'host_since', 'host_url', 'host_location']