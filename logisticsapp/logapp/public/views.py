
from rest_framework.views import APIView
from django.http import JsonResponse
from app.conf import base as settings
import simplejson as json
import os
from tools.publish import publishCatalogStructureJSON,publishHRStructureJSON



class OrgStructure(APIView):
    '''
    Send JSON data simply
    '''
    permission_classes = []

    def get(self,request,format=None):
        hr_json_file=os.path.join(settings.BASE_DIR,'static/public/hr.json')
        retry_again=False
        with open(hr_json_file) as data:
            try:
                json_data=json.load(data)
            except:
                #probably empty. publish it
                publishHRStructureJSON(add_notify=False)
                retry_again=True

        if retry_again:
                with open(hr_json_file) as data:
                    try:
                        json_data=json.load(data)
                    except:
                        #probably empty. probably no data in the system
                        json_data=[]

        return JsonResponse(json_data,status=200)


class ItemsStructure(APIView):
    '''
    Send JSON data simply
    '''
    permission_classes = []

    def get(self,request,format=None):

        catalog_json_file=os.path.join(settings.BASE_DIR,'static/public/items.json')
        retry_again=False
        with open(catalog_json_file) as data:
            try:
                json_data=json.load(data)
            except:
                #empty probably. republish then try
                publishCatalogStructureJSON(add_notify=False)
                retry_again=True

        if retry_again:
            with open(catalog_json_file) as data:
                try:
                    json_data=json.load(data)
                except:
                    #empty probably. republish then try
                    json_data=[]
                               



        return JsonResponse(json_data,status=200)
     



 