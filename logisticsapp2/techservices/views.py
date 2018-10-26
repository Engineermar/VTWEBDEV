
from tools.formtools import createErrorDataJSON

from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse

from logistic.models import IncomingItem,TechnicalService


from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo


from techservices.serializers import TechnicalServiceSerializer


class Services(APIView):
	'''
	Services done on it. Manager and Logistic Officer Only
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,tag,searchby,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['can_view_tech_services'])

		if have_right:
			#get the info now
			try:
				filters={'product__kind':'Non-consumable'}

				

				if searchby=='tag':
					filters['tag']=tag
				elif searchby=='rlrc':
					filters['institution_code']=tag
				elif searchby=='manf':
					filters['manf_serial']=tag

				item=IncomingItem.objects.values('id','product__asset_code','arrivedon','brand__name','manf__name','price','tag','current_status','arrival_status','product__name','product__category__name').get(**filters)

				reply['item']=item

				reply['services']=list(TechnicalService.objects.filter(item_id=item['id']).values('id','createdon','monetary_value','manpower_value','action','comment','arrivedon','processedby__first_name','processedby__last_name','new_status').order_by('-arrivedon',))

		
				status=200
			except:
				reply['detail']=_('ErrorItemNotFound')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class AddService(APIView):
	'''
	Add service that was done to it
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,tag,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['add_technicalservice'])

		if have_right:
			#get the info now
			data=request.data
			serializer=TechnicalServiceSerializer(data=data,current_id=0,item_tag=tag)
			#is it valid
			if serializer.is_valid():
				content=serializer.validated_data
				info=TechnicalService(item_id=content['item_id'],processedby_id=request.user.id,comment=content['comment'],manpower_value=content['manpower_value'],monetary_value=content['monetary_value'],action=content['action'],arrivedon=content['arrivedon'],new_status=content['new_status'] )
				info.save()
				if info:
					reply['new_id']=info.id
					reply['tech_first_name']=request.user.first_name
					reply['tech_last_name']=request.user.last_name
					reply['detail']=_('ServiceAddOk')
					status=200
					if content['new_status']!='Unchanged':
						#the status of the item is now changed. Weather it is in hand or store, change its CURRENT STATUS
						item=IncomingItem.objects.get(pk=info.item_id)
						item.current_status=content['new_status']
						item.save();
				else:
					reply['detail']=_('ErrorServiceAddFailed')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class EditService(APIView):
	'''
	Edit service information of an existing item. Send the system tag of the item and id of the service to edit
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,tag,service_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['change_technicalservice'])

		if have_right:
			#get the info now
			data=request.data
			serializer=TechnicalServiceSerializer(data=data,current_id=service_id,item_tag=tag)
			#is it valid
			if serializer.is_valid():
				content=serializer.validated_data

				try:

					info=TechnicalService.objects.get(pk=service_id,item__tag=tag)
					#make the necessary changes now
					info.comment=content['comment']
					info.manpower_value=content['manpower_value']
					info.monetary_value=content['monetary_value']
					info.action=content['action']
					info.arrivedon=content['arrivedon']
					info.new_status=content['new_status']
					info.save()
					status=200
					reply['detail']=_('ServiceUpdateOk')
					
					if content['new_status']!='Unchanged':
						#the status of the item is now changed. Weather it is in hand or store, change its CURRENT STATUS
						item=IncomingItem.objects.get(pk=info.item_id)
						item.current_status=content['new_status']
						item.save();

				except:
					reply['detail']=_('ErrorServiceUpdateFailed')


			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class DeleteService(APIView):
	'''
	Delete service information of an existing item. Send the system tag of the item and id of the service to delete
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,tag,service_id,format=None):
		reply={}
		status=400
		have_right=userIsPermittedTo(request.user.id,['delete_technicalservice'])

		if have_right:
			#get the info now
			
			try:
				info=TechnicalService.objects.get(pk=service_id,item__tag=tag)
				#delete
				info.delete()
				status=200
				reply['detail']=_('ServiceDeleteOk')
			except:
				reply['detail']=_('ServiceDeleteFailed')
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)







