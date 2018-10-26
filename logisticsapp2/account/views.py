from tools.formtools import createErrorDataJSON

from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse


from django.contrib.auth.models import User
from hr.models import Employee
from django.utils.translation import ugettext_lazy as _

from users.serializers import EmployeeSerializer
from account.serializers import ChangePwdSerializer





class EditProfile(APIView):
	'''
	Edit my profile
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=200

		#get his profile
		reply['profile']=Employee.objects.values('title','gender','idcard','rlrc_id','user__email','user__first_name','user__last_name','phone').get(user_id=request.user.id)
	


		return JsonResponse(reply,status=status)


	def post(self,request,format=None):
		reply={}
		status=400

		data=request.data

		serializer=EmployeeSerializer(data=data,user_id=request.user.id)

		if serializer.is_valid():
			content=serializer.validated_data

			try:

				user=User.objects.get(pk=request.user.id)
				user.email=content['email']
				user.username=content['email']
				user.first_name=content['first_name']
				user.last_name=content['last_name']
				user.save()

				emp=Employee.objects.get(user_id=request.user.id)
				emp.phone=content['phone']
				emp.title=content['title']
				emp.idcard=content['idcard']
				emp.rlrc_id=content['rlrc_id']
				emp.gender=content['gender']
				emp.save()

				reply['detail']=_('ProfileUpdateOk')
				status=200
			except:
				reply['detail']=_('ErrorProfileUpdate')
			

		else:
			reply['detail']=createErrorDataJSON(serializer.errors)


		return JsonResponse(reply,status=status)



class ChangePwd(APIView):
	'''
	Give user the chance to change password
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		return JsonResponse({'detail':True},status=200)

	def post(self,request,format=None):
		reply={}
		status=400
		#data=request.data
		data=request.data
		serializer=ChangePwdSerializer(data=data,user=request.user)

		if serializer.is_valid():
			#it is valid
			content=serializer.validated_data
			request.user.set_password(content['password'])
			request.user.save()
			status=200
			reply['detail']=_('SecurityPasswordUpdateOk')
		else:
			
			reply['detail']=createErrorDataJSON(serializer.errors) 
			
			

		return JsonResponse(reply,status=status)



