
from tools.formtools import createErrorDataJSON

from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse

from django.db.models import Q

from hr.models import EmployeePosition,Head,Department,Division,Unit,Profession,Office
from logistic.models import OutgoingInvoice, ReturnItemInvoice


from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo

from hr.serializers import HeadSerializer,DepartmentSerializer,DivisionSerializer,UnitSerializer,ProfessionSerializer,OfficeSerializer

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import app.appsettings as appsettings

from tools.publish import publishHRStructureJSON


class OfficesList(APIView):
	'''
	List of offices in a given head/dept/divsision/unit
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,hr_kind,hr_id,format=None):
		status=400
		reply={}

		have_right=userIsPermittedTo(request.user.id,['add_office','change_office','delete_office'])
		if have_right:
			filters={'head_id':None,'dept_id':None,'division_id':None,'unit_id':None}
			if hr_kind=='h':
				#in head
				filters['head_id']=hr_id
			elif hr_kind=='d':
				filters['dept_id']=hr_id
			elif hr_kind=='v':
				filters['division_id']=hr_id
			elif hr_kind=='u':
				filters['unit_id']=hr_id

			reply['detail']=list(Office.objects.filter(**filters).values('id','name','head_id','dept_id','division_id','unit_id').order_by('name'))
			status=200

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class OfficeAdd(APIView):
	'''
	Add a new office
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		status=400
		reply={}

		have_right=userIsPermittedTo(request.user.id,['add_office',])
		if have_right:
			data=request.data
			serializer=OfficeSerializer(data=data)

			if serializer.is_valid():
				content=serializer.validated_data
				hr_id=content['office_for_id']

				fields={'head_id':None,'dept_id':None,'division_id':None,'unit_id':None,'name':content['name']}

				if content['office_for']=='h':
					#in head
					fields['head_id']=hr_id
				elif content['office_for']=='d':
					fields['dept_id']=hr_id
				elif content['office_for']=='v':
					fields['division_id']=hr_id
				elif content['office_for']=='u':
					fields['unit_id']=hr_id


				office=Office(**fields)
				office.save()
				if office:
					reply['id']=office.id
					reply['detail']=_('HROfficeAddedOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('HRErrorOfficeAdding')


			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class OfficeEdit(APIView):
	'''
	Edit office information, which is to change name and location
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,id,format=None):
		status=400
		reply={}

		have_right=userIsPermittedTo(request.user.id,['change_office',])
		if have_right:
			data=request.data
			serializer=OfficeSerializer(data=data,office_id=id)

			if serializer.is_valid():
				content=serializer.validated_data
				hr_id=content['office_for_id']
				try:
					office=Office.objects.get(pk=id)
		
					office.name=content['name']
					if content['office_for']=='h':
						office.head_id=hr_id
					elif content['office_for']=='d':
						office.dept_id=hr_id
					elif content['office_for']=='v':
						office.division_id=hr_id
					elif content['office_for']=='u':
						office.unit_id=hr_id

					office.save()
					status=200
					reply['detail']=_('HROfficeUpdateOk')
					publishHRStructureJSON(user_id=request.user.id)

				except:
					reply['detail']=_('HRErrorofficeMissing')
				


			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class OfficeDelete(APIView):
	'''
	Delete office information
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,id,format=None):
		status=400
		reply={}

		have_right=userIsPermittedTo(request.user.id,['delete_office',])
		if have_right:
			try:
				office=Office.objects.get(pk=id)
				errmsg=''
				if OutgoingInvoice.objects.filter(Q(office_id=id)  | Q(transfered_from_office_id=id)).exists():
					errmsg=_('ErrorHROfficeDeleteDepedencyData')

				if not errmsg:
					if ReturnItemInvoice.objects.filter(Q(office_id=id)).exists():
						errmsg=_('ErrorHROfficeDeleteDepedencyData')

				if errmsg:
					reply['detail']=errmsg
				else:

					office.delete()

					status=200
					reply['detail']=_('HROfficeDeleteOk')
					publishHRStructureJSON(user_id=request.user.id)

			except:
				reply['detail']=_('ErrorHROfficeDelete')
				

		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class HeadsList(APIView):
	'''
	This module display list of heads for the purposes of management
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])
			
		if have_right:
		

			reply['detail']=list(Head.objects.all().values('id','name','active').order_by('name',))
			status=200		
		else:

			reply['detail']	=_('NoRight')
		
		return JsonResponse(reply,status=status)

class HeadInformation(APIView):
	'''
	Return information about a specific head
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400

		try:
			reply['detail']=Head.objects.values('id','name','active').get(pk=record_id)
			status=200
		except:
			reply['detail']=_('ErrorHRHeadNotFound')
					
		

		return JsonResponse(reply,status=status)

class HeadAdd(APIView):
	'''
	Add a new Head. Add Head
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_head'])

		if have_right:
			#process
			data=request.data
			serializer=HeadSerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Head(name=content['name'],active=content['active'], added_by_id=request.user.id)
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('HRHeadAddOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorHRHeadAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class HeadEdit(APIView):
	'''
	Edit an existing Head. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_head'])

		if have_right:
			#process
			data=request.data
			serializer=HeadSerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					head=Head.objects.get(pk=record_id)
					head.name=content['name']
					head.active=content['active']
					head.save()
					status=200
					reply['detail']=_('HRHeadUpdateOk')
					publishHRStructureJSON(user_id=request.user.id)
				except:
					reply['detail']=_('ErrorHRHeadNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class HeadDelete(APIView):
	'''
	Delete the requested head. For head to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_head'])

		if have_right:
			#process

			try:
				head=Head.objects.get(pk=record_id)
				errmsg=''
				if OutgoingInvoice.objects.filter(Q(head_id=record_id) | Q(head__office_head__head_id=record_id) | Q(department__head_id=record_id) | Q(division__department__head_id=record_id) | Q(unit__division__department__head_id=record_id) | Q(transfered_from_head_id=record_id) | Q(transfered_from_head__office_head__head_id=record_id) | Q(transfered_from_department__head_id=record_id) | Q(transfered_from_division__department__head_id=record_id) | Q(transfered_from_unit__division__department__head_id=record_id)).exists():
					errmsg=_('ErrorHRHeadDeleteDepedencyData')

				if not errmsg:
					if ReturnItemInvoice.objects.filter(Q(head_id=record_id)  | Q(head__office_head__head_id=record_id) | Q(department__head_id=record_id) | Q(division__department__head_id=record_id) | Q(unit__division__department__head_id=record_id)).exists():
						errmsg=_('ErrorHRHeadDeleteDepedencyData')



				if errmsg:
					reply['detail']=errmsg
				else:
					head.delete()
					reply['detail']=_('HRHeadDeleteOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
			except:
				reply['detail']=_('ErrorHRHeadDelete')

			

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



'''
* DEPARTMENTS MANAGEMENT AND VIEWING
'''

class DepartmentsList(APIView):
	'''
	This module display list of departments. The role is limited to Manager,Logistic Officer, DAF Officer Only.
	Note that we can view all departments if head_id=0 or just the departments in head_id
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,head_id,format=None):
		reply={}
		status=400

		head_id=int(head_id)

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])


		if have_right:
			#return list of Departments now
			filters={'head_id':head_id}
			

			fields=['id','name','head_id','active']

			reply['detail']=list(Department.objects.filter(**filters).values(*fields).order_by('name',))
			
			status=200			
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class DeparmentInformation(APIView):
	'''
	Return information about a specific department.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400


		try:

			reply['detail']=Department.objects.values('id','name','active','head_id','head__name').get(pk=record_id)
			status=200
		except:
			reply['detail']=_('ErrorHRDepartmentNotFound')
					
		

		return JsonResponse(reply,status=status)

class DepartmentAdd(APIView):
	'''
	Add a new Department to Head. Only Administrator can do that. We can add to an inactive Head, long as it exists.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,head_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_department'])

		if have_right:
			#process
			data=request.data
			serializer=DepartmentSerializer(data=data,current_id=0,head_id=head_id)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Department(name=content['name'],active=content['active'],head_id=head_id,added_by_id=request.user.id)
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('HRDepartmentAddOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorHRDepartmentAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class DepartmentEdit(APIView):
	'''
	Edit an existing Deparment. Only Administrator can do that.
	Note here: head_id could be a new head_id or the same existing one
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,head_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_department'])

		if have_right:
			#process
			data=request.data
			serializer=DepartmentSerializer(data=data,current_id=record_id,head_id=head_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					department=Department.objects.get(pk=record_id)
					department.name=content['name']
					department.active=content['active']
					department.head_id=head_id
					department.save()
					status=200
					publishHRStructureJSON(user_id=request.user.id)
					reply['detail']=_('HRDepartmentUpdateOk')
				except:
					reply['detail']=_('ErrorHRDepartmentNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class DepartmentDelete(APIView):
	'''
	Delete the requested department. For department to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,head_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_department'])

		if have_right:
			#process

			try:
				department=Department.objects.get(pk=record_id,head_id=head_id)
				#delete here
				errmsg=''
				if OutgoingInvoice.objects.filter(Q(department_id=record_id) | Q(department__office_dept__dept_id=record_id)  | Q(division__department_id=record_id) | Q(unit__division__department_id=record_id) | Q(transfered_from_department_id=record_id) | Q(transfered_from_department__office_dept__dept_id=record_id) | Q(transfered_from_division__department_id=record_id) | Q(transfered_from_unit__division__department_id=record_id)).exists():
					errmsg=_('ErrorHRDepartmentDeleteDepedencyData')

				if not errmsg:
					if ReturnItemInvoice.objects.filter(Q(department_id=record_id)  | Q(department__office_dept__dept_id=record_id) | Q(division__department_id=record_id) | Q(unit__division__department_id=record_id)).exists():
						errmsg=_('ErrorHRDepartmentDeleteDepedencyData')				

				if errmsg:
					reply['detail']=errmsg
				else:
					department.delete()
					reply['detail']=_('HRDepartmentDeleteOk')
					publishHRStructureJSON(user_id=request.user.id)
					status=200
			except:
				reply['detail']=_('ErrorHRDepartmentDelete')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


'''
DIVISIONS MANAGEMENT AND LISTING
'''
class DivisionsList(APIView):
	'''
	This module display list of divisions. The role is limited to Manager,Logistic Officer, DAF Officer Only.
	Note that we can view all divisions if department_id=0 or just the divisions in department_id
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,department_id,format=None):
		reply={}
		status=400

		department_id=int(department_id)

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])


		if have_right:
			#return list of Divisions now
			filters={'department_id':department_id}
			

			fields=['id','name','department_id','active']

			reply['detail']=list(Division.objects.filter(**filters).values(*fields).order_by('name',))
			
			status=200			
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)

class DivisionInformation(APIView):
	'''
	Return information about a specific division.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,record_id,format=None):
		reply={}
		status=400




		try:

			reply['detail']=Division.objects.values('id','name','active','department__head_id','department__head__name','department_id','department__name').get(pk=record_id)
			status=200
		except:
			reply['detail']=_('ErrorHRDivisionNotFound')
					
	

		return JsonResponse(reply,status=status)

class DivisionAdd(APIView):
	'''
	Add a new Division to Department. Only Administrator can do that. We can add to an inactive Department, long as it exists.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,department_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_division'])

		if have_right:
			#process
			data=request.data
			serializer=DivisionSerializer(data=data,current_id=0,department_id=department_id)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Division(name=content['name'],active=content['active'],department_id=department_id,added_by_id=request.user.id)
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('HRDivisionAddOk')
					publishHRStructureJSON(user_id=request.user.id)
					status=200
				else:
					reply['detail']=_('ErrorHRDivisionAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class DivisionEdit(APIView):
	'''
	Edit an existing Division. Only Administrator can do that.
	Note here: department_id could be a new department_id or the same existing one
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,department_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_division'])

		if have_right:
			#process
			data=request.data
			serializer=DivisionSerializer(data=data,current_id=record_id,department_id=department_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					division=Division.objects.get(pk=record_id)
					division.name=content['name']
					division.active=content['active']
					division.department_id=department_id
					division.save()
					status=200
					publishHRStructureJSON(user_id=request.user.id)
					reply['detail']=_('HRDivisionUpdateOk')
				except:
					reply['detail']=_('ErrorHRDivisionNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)


class DivisionDelete(APIView):
	'''
	Delete the requested division. For division to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,department_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_division'])

		if have_right:
			#process
			
			
			try:
				division=Division.objects.get(pk=record_id,department_id=department_id)
				errmsg=''
				if OutgoingInvoice.objects.filter(Q(division_id=record_id) | Q(division__office_division__division_id=record_id) | Q(unit__division_id=record_id)  | Q(transfered_from_division_id=record_id) |Q(transfered_from_division__office_division__division_id=record_id) | Q(transfered_from_unit__division_id=record_id)).exists():
					errmsg=_('ErrorHRDivisionDeleteDepedencyData')
				if not errmsg:
					if ReturnItemInvoice.objects.filter(Q(division_id=record_id)  | Q(division__office_division__division_id=record_id) | Q(unit__division_id=record_id)).exists():
						errmsg=_('ErrorHRDivisionDeleteDepedencyData')

				if errmsg:
					reply['detail']=errmsg
				else:
					division.delete(user_id=request.user.id)
					reply['detail']=_('HRDivisionDeleteOk')
					publishHRStructureJSON()
					status=200

			except:
				reply['detail']=_('ErrorHRDivisionDelete')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



'''
Unit Management and Listing
'''

class UnitsList(APIView):
	'''
	This module display list of units. The role is limited to Manager,Logistic Officer, DAF Officer Only.
	Note that we can view all units if division_id=0 or just the units in division_id
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,division_id,format=None):
		reply={}
		status=400

		division_id=int(division_id)

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])


		if have_right:
			#return list of Units now
			filters={'division_id':division_id}
			

			fields=['id','name','division_id','active']
		
			reply['detail']=list(Unit.objects.filter(**filters).values(*fields).order_by('name',))
			
			status=200			
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)



class UnitAdd(APIView):
	'''
	Add a new Unit to Department. Only Administrator can do that. We can add to an inactive Department, long as it exists.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,division_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_unit'])

		if have_right:
			#process
			data=request.data
			serializer=UnitSerializer(data=data,current_id=0,division_id=division_id)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Unit(name=content['name'],active=content['active'],division_id=division_id,added_by_id=request.user.id)
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('HRUnitAddOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorHRUnitAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class UnitEdit(APIView):
	'''
	Edit an existing Unit. Only Administrator can do that.
	Note here: division_id could be a new division_id or the same existing one
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,division_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_unit'])

		if have_right:
			#process
			data=request.data
			serializer=UnitSerializer(data=data,current_id=record_id,division_id=division_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					unit=Unit.objects.get(pk=record_id)
					unit.name=content['name']
					unit.active=content['active']
					unit.division_id=division_id
					unit.save()
					status=200
					publishHRStructureJSON(user_id=request.user.id)
					reply['detail']=_('HRUnitUpdateOk')
				except:
					reply['detail']=_('ErrorHRUnitNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class UnitDelete(APIView):
	'''
	Delete the requested unit. For unit to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,division_id,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_unit'])

		if have_right:
			#process

			try:
				unit=Unit.objects.get(pk=record_id,division_id=division_id)
				errmsg=''
				if OutgoingInvoice.objects.filter(Q(unit_id=record_id) | Q(unit__office_unit__unit_id=record_id) | Q(transfered_from_unit_id=record_id) | Q(transfered_from_unit__office_unit__unit_id=record_id)).exists():
					errmsg=_('ErrorHRUnitDeleteDepedencyData')
				else:
					if ReturnItemInvoice.objects.filter(Q(unit_id=record_id)  | Q(unit__office_unit__unit_id=record_id)).exists():
						errmsg=_('ErrorHRUnitDeleteDepedencyData')


				if errmsg:
					reply['detail']=errmsg
				else:
					unit.delete()
					reply['detail']=_('HRUnitDeleteOk')
					publishHRStructureJSON(user_id=request.user.id)

					status=200
			except:
				reply['detail']=_('ErrorHRUnitDelete')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)




class ProfessionsList(APIView):
	'''
	This module display list of professions. The role is limited to Manager,Logistic Officer, DAF Officer Only.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,paginated,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])


		if have_right:
			#return list of Heads now
			
			
			filters={}

			

			records=Profession.objects.filter(**filters).values('id','name','active').order_by('name',)


			if int(paginated)==0:
				reply['detail']=list(records)
				status=200
			else:
				status=200
				try:
					
					page=request.query_params.get('page',1)
					paginator=Paginator(records,appsettings.APPSET_NUMBER_OF_JOBS_TOSHOW)
					data=paginator.page(page)
				except PageNotAnInteger:
					data=paginator.page(1)
				except EmptyPage:
					data=paginator.page(paginator.num_pages)

				except:
					data=None
					status=400
					reply['detail']=(_('InvalidPath'))

				if status==200:
					reply['detail']=list(data)
					reply['total_num_of_pages']=paginator.num_pages
					reply['total_rows_found']=paginator.count
					reply['total_per_page_allowed']=appsettings.APPSET_NUMBER_OF_JOBS_TOSHOW
					reply['current_page']=page				

						
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)



class ProfessionAdd(APIView):
	'''
	Add a new Profession. Only Administrator and Logistic Officer can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_profession'])

		if have_right:
			#process
			data=request.data
			serializer=ProfessionSerializer(data=data,current_id=0)
			if serializer.is_valid():
				content=serializer.validated_data

				add_new=Profession(name=content['name'],active=content['active'], added_by_id=request.user.id)
				add_new.save()
				if add_new:
					reply['new_id']=add_new.id
					reply['detail']=_('HRProfessionAddOk')
					status=200
					publishHRStructureJSON(user_id=request.user.id)
				else:
					reply['detail']=_('ErrorHRProfessionAddError')
			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class ProfessionEdit(APIView):
	'''
	Edit an existing Profession. Only Administrator can do that.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_profession'])

		if have_right:
			#process
			data=request.data
			serializer=ProfessionSerializer(data=data,current_id=record_id)
			if serializer.is_valid():
				content=serializer.validated_data
				#does the row exist at or not?
				try:
					profession=Profession.objects.get(pk=record_id)
					profession.name=content['name']
					profession.active=content['active']
					profession.save()
					status=200
					reply['detail']=_('HRProfessionUpdateOk')
					publishHRStructureJSON(user_id=request.user.id)
				except:
					reply['detail']=_('ErrorHRProfessionNotFound')

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)



class ProfessionDelete(APIView):
	'''
	Delete the requested profession. For profession to be deleted, there must not be transactional history under it.
	'''
	permission_classes = [TokenHasReadWriteScope]
	def post(self,request,record_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_profession'])

		if have_right:
			#process

			if EmployeePosition.objects.filter(job_id=record_id).exists():
				reply['detail']=_('ErrorHRProfessionDeletePositionsExist')

			else:

				try:
					profession=Profession.objects.get(pk=record_id)
					#delete here. Check data here
					

					profession.delete()
					reply['detail']=_('HRProfessionDeleteOk')
					publishHRStructureJSON(user_id=request.user.id)

					status=200
				except:
					reply['detail']=_('ErrorHRProfessionNotFound')

			

		else:
			reply['detail']=_('NoRight')



		return JsonResponse(reply,status=status)







class Publish(APIView):
	'''
	Organizational Structures often stay the same and unchanged for a long period of time. As such, it is an overkill to query the datababase for HR
	related information over and over again except during management.

	E.g. when registering a new user/employee, we ask for HR information such as the unit and profession they work for. The process can be reptitive
	and costly in relation to database operation.

	Hence, we publish HR structure to JSON which can be consumed direclty and rather quickly when needed.

	Only active data should be shown.

	Only Manager can do processing.
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		
		publishHRStructureJSON(add_notify=False)

		status=200
		reply['detail']=_('HRPublished')



		return JsonResponse(reply,status=status)



