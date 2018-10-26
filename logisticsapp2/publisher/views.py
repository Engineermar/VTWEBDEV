
from django.utils.translation import ugettext_lazy as _


from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse
from tools.publish import publishCatalogStructureJSON,publishHRStructureJSON


class Publish(APIView):
	'''
	Publish Catalog and HR Structure to JSON for public consumption. This is public.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,publish_what,format=None):

		publishHRStructureJSON(add_notify=False)
		publishCatalogStructureJSON(add_notify=False)
		
		'''
		if publish_what=='1':
			#publis hr
			publishHRStructureJSON()
		elif publish_what=='2':
			publishCatalogStructureJSON()

		'''



		return JsonResponse({'detail':_('PublishDone')},status=200)

