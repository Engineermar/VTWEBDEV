from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from airbnb.models import BnbHost, BnbListing, BnbReview
from airbnb.forms import BnbHostForm
from . import sentiment
import json, traceback

def home(request):
    return HttpResponse("Welcome to AirBNB")

def host(request):
    objBnbHost = BnbHost.objects.all().order_by('-host_id')
    objBnbListing = BnbListing.objects.all()
    coordinates = list(objBnbListing.values_list('latitude','longitude'))
    objBnbHosFields = [f.name.replace('_',' ').title() for f in BnbHost._meta.fields]
    #print(objBnbHost.values()[0])
    return render(request, 'airbnb_host.html', context={"objBnbHost":objBnbHost.values(),"objBnbHosFields":objBnbHosFields, "coordinates": json.dumps(coordinates)})
    
def listing(request,host_id):
    print(request.GET)
    if host_id!='all':
        objBnbListing = BnbListing.objects.filter(host_id=host_id)
    else:
        objBnbListing = BnbListing.objects.all()
    objBnbListingFields = [f.name.replace('_',' ').title() for f in BnbListing._meta.fields]
    coordinates = list(objBnbListing.values_list('latitude','longitude'))
    return render(request, 'airbnb_listing.html', context={"objBnbListing":objBnbListing.values(),"objBnbListingFields":objBnbListingFields, "host_id": host_id,'coordinates': json.dumps(coordinates)})

def review(request, listing_id):
    objBnbReview = BnbReview.objects.filter(listing_id=listing_id)
    objBnbReviewFields = [f.name.replace('_',' ').title() for f in BnbReview._meta.fields]
    valuesobjBnbReview = objBnbReview.values()
    #print(objBnbHost.values()[0])
    sentiment.sentiment(valuesobjBnbReview)
    return render(request, 'airbnb_review.html', context={"objBnbReview":valuesobjBnbReview,"objBnbReviewFields":objBnbReviewFields, "listing_id": listing_id})
    
def plot(request):
    objBnbListingList=[['number_of_reviews','price']]
    objBnbListing = BnbListing.objects.all().order_by('price')
    i=0
    ## SCATTER
    for obj in objBnbListing:
        try:
            int_number_of_reviews = float(obj.number_of_reviews)
            int_price = float(obj.price.replace("$","").replace(",","").strip())
            if int_number_of_reviews>25 and int_price>500.0:
                objBnbListingList.append([int_number_of_reviews, int_price])
        except:
            print(i)
            print(traceback.format_exc())
            i=i+1
    ## HISTOGRAM - ZIP
    zip_list = [str(z) for z in list(objBnbListing.order_by('zip').values_list("zip",flat=True).distinct())]
    zip_dict_list = [["Zipcode","Number of listings"]]
    for zip in zip_list:
        if zip:
            zip_dict_list.append([zip, objBnbListing.filter(zip=zip).count()])
    return render(request, 'graph.html', context={"objBnbListingList": json.dumps(objBnbListingList), "zip_dict_list": json.dumps(zip_dict_list)})
    
def add_host(request):
    if request.method=='GET':
        objBnbHostForm = BnbHostForm()
        return render(request, 'airbnb_host_update.html', context={"objBnbHostForm":objBnbHostForm})
    else:
        host_id_last=BnbHost.objects.all().order_by("-pk")[0].pk
        host_id = host_id_last+1
        objBnbHostForm = BnbHostForm(request.POST)
        objBnbHost = objBnbHostForm.save(commit=False)
        objBnbHost.pk=host_id
        objBnbHost.save()
        return HttpResponseRedirect('/airbnb/host')
        
def edit_host(request,host_id):
    objBnbHost = BnbHost.objects.get(pk=host_id)
    if request.method=='GET':
        objBnbHostForm = BnbHostForm(instance=objBnbHost)
        return render(request, 'airbnb_host_update.html', context={"objBnbHostForm":objBnbHostForm})
    else:
        objBnbHostForm = BnbHostForm(request.POST, instance=objBnbHost)
        objBnbHost = objBnbHostForm.save(commit=False)
        objBnbHost.pk=host_id
        objBnbHost.save()
        return HttpResponseRedirect('/airbnb/host')