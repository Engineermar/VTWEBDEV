from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from logistic.models import IncomingItem



class FindItem(APIView):
	'''
	Find an item by tag. Note this is not considered sensitive information hence all we care about is an active token.
	Just return information of the item briefly. This is only for assets and only a single item
	'''

	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400


		tag=request.query_params.get('tag','').strip() #the actual vaue
		searchby=request.query_params.get('searchby','tag')

		filters={'product__kind':'Non-consumable'}

		

		if searchby=='tag':
			filters['tag']=tag
		elif searchby=='rlrc':
			filters['institution_code']=tag
		elif searchby=='manf':
			filters['manf_serial']=tag
		
	
		try:
			
			item=IncomingItem.objects.values('id','product__asset_code','product__kind','arrivedon','brand__name','manf__name','tag','arrival_status','current_status','product__name','product__category__name','price','manf_serial','institution_code').get(**filters)
			#item existing. Now based on level get additional data
			reply['item']=item
			status=200
		except:
			reply['detail']=_('ErrorItemMissing')


		return JsonResponse(reply,status=status)
