

from rest_framework.views import APIView
from django.http import JsonResponse
from hr.models import Notification



class CheckDataUpdates(APIView):
	'''
	Check for new notifications. Front-end checks for those messages automatically. We use Notification Model.

	We just ntofiy the user there are some changes in the Catalog or HR structure of hte system so he updates the system; not the individual messages
	'''
	permission_classes = []

	def get(self,request,format=None):
		reply={'data':0}
		if Notification.objects.filter(is_counted=0).exclude(user_id=request.user.id).exists():
			reply['data']=1
		
		Notification.objects.filter(is_counted=0).update(is_counted=1)

		return JsonResponse(reply,status=200)