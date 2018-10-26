

from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse


from django.db.models import Count, F


from logistic.models import OutgoingInvoice







class Employee(APIView):
	'''
	Home page or dashboard data for Employee roles. This is called by default
	'''
	permission_classes = [TokenHasReadWriteScope]


	def get(self,request,format=None):
		reply={}
		status=400
		
		#show items that are currently under his name in the form of a summary E.g. Desktop: 5, Laptop : 3 etc
		reply['in_hand']=list(OutgoingInvoice.objects.filter(give_to__user_id=request.user.id,receipent_type='Employee',outgoingitem_outgoinginvoice__ownership_status__in=[1,5]).annotate(product_name=F('outgoingitem_outgoinginvoice__item__product__name')).values('product_name').annotate(total=Count('outgoingitem_outgoinginvoice')).order_by('product_name',))
		reply['transaction_history']=list(OutgoingInvoice.objects.filter(give_to__user_id=request.user.id,receipent_type='Employee',outgoingitem_outgoinginvoice__ownership_status__in=[1,2,5]).annotate(product_name=F('outgoingitem_outgoinginvoice__item__product__name'),status=F('outgoingitem_outgoinginvoice__ownership_status')).values('status','product_name').annotate(total=Count('outgoingitem_outgoinginvoice')).order_by('status','product_name'))
		#what you consume:
		reply['consumed']=list(OutgoingInvoice.objects.filter(give_to__user_id=request.user.id,receipent_type='Employee',outgoingitem_outgoinginvoice__item__product__kind='Consumable').annotate(measure=F('outgoingitem_outgoinginvoice__item__product__measurement_unit'),product_name=F('outgoingitem_outgoinginvoice__item__product__name')).values('product_name','measure').annotate(total=Count('outgoingitem_outgoinginvoice')).order_by('product_name',))
		status=200


		return JsonResponse(reply,status=status)
