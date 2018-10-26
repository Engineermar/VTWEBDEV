'''
 * Rwanda Law Reform Comission
 *
 * Developed by Sium, Kigali, Rwanda 2016-2017. All Rights Reserved
 *
 * This content is protected by national and international patent laws.
 *
 * Possession and access to this content is granted exclusively to Developers
 * of RLRC and Sium, while full ownership is granted only to Rwanda Law Reform Comission.
 
 *
 * @package	RLWC - LRC
 * @author	Kiflemariam Sium (kmsium@gmail.com || sium@go.rw || sium@iconicdatasystems.com)
 * @copyright	Copyright (c) RLCR Limited, 2017
 * @license	http://
 * @link	http://
 * @since	Version 1.0.0
 * @filesource
 '''
from hr.models import Head,Department,Division,Unit,Profession,Office
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from validation.validators import validateCharacters



class HeadSerializer(serializers.Serializer):
	'''
	Make sure Head information is ok before you save it
	'''
	name=serializers.CharField(max_length=60,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(HeadSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')

		print(active)

		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorHRHeadNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now
				ensure_unique={}
				if self.current_row_id>0:
					ensure_unique['id']=self.current_row_id

				if Head.objects.filter(name=name).exclude(**ensure_unique).exists():
					errmsg['name']=_('ErrorHRHeadNameExists')



		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data


class OfficeSerializer(serializers.Serializer):
	'''
	Make sure Office information is correct
	'''
	name=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=70)#
	office_for=serializers.CharField(max_length=1)#
	office_for_id=serializers.IntegerField(default=0) #
	
	
	def __init__(self,*args,**kwargs):
		self.current_id=int(kwargs.pop('office_id', 0))
		super(OfficeSerializer, self).__init__(*args, **kwargs)


	def validate(self,data):
		#validate the data here

		errmsg={}

		exclude={} #used during editing only


		#we can check other data now
		name=data.get('name','').strip().capitalize()
		office_for=data.get('office_for','').lower().strip()
		office_for_id=data.get('office_for_id',0)

		if len(name)<3:
			errmsg['name']=_('ErrorHROfficeNameTooShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters
		


		if self.current_id>0:
			exclude['id']=self.current_id



		unique_name_check={}

		if office_for=='u':	
			#selected a unit. So office is in happening in Unit level of the HR
			if not Unit.objects.filter(pk=office_for_id).exists():
				errmsg['office_for']=_('ErrorEmpRegisterHRInvalidUnit')
			else:
				unique_name_check['unit_id']=office_for_id
			


		elif office_for=='v':

			
			if not Division.objects.filter(pk=office_for_id).exists():
				errmsg['office_for']=_('ErrorEmpRegisterHRInvalidDivision')
			else:
				unique_name_check['division_id']=office_for_id

		elif office_for=='d':
			if not Department.objects.filter(pk=office_for_id).exists():
				errmsg['office_for']=_('ErrorEmpRegisterHRInvalidDept')
			else:
				unique_name_check['dept_id']=office_for_id

		elif office_for=='h':

			if not Head.objects.filter(pk=office_for_id).exists():
				errmsg['office_for']=_('ErrorEmpRegisterHRInvalidHead')
			else:
				unique_name_check['head_id']=office_for_id
		else:
			errmsg['office_for']=_('ErrorHROfficeMissing')


		if unique_name_check and not errmsg:
			unique_name_check['name']=name
			if Office.objects.filter(**unique_name_check).exclude(**exclude).exists():
				errmsg['name']=_('HRErrorOfficeExists')
	

		if errmsg:
			raise serializers.ValidationError(errmsg)

	



		return data


class DepartmentSerializer(serializers.Serializer):
	'''
	Make sure Department information is ok before you save it
	'''
	name=serializers.CharField(max_length=60,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.head_id=int(kwargs.pop('head_id',0))
		super(DepartmentSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		

		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorHRDepartmentNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now. Make sure the head exists first
				if self.head_id<=0:
					errmsg['head']=_('ErrorHRDepartmentInvalidHead')
				else:
					try:
						head=Head.objects.get(pk=self.head_id)
						#head is ok. Ensure the name of the department is unique within the Head now
						ensure_unique={}
						
						if self.current_row_id>0:
							ensure_unique['id']=self.current_row_id
							ensure_unique['head_id']=self.head_id

						if Department.objects.filter(name=name,head_id=self.head_id).exclude(**ensure_unique).exists():
							errmsg['name']=_('ErrorHRDepartmentNameExists') % {'head_name':head.name,'dept_name':name}

					except:
						errmsg['head']=_('ErrorHRDepartmentInvalidHead')

				




		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data


class DivisionSerializer(serializers.Serializer):
	'''
	Make sure Division information is ok before you save it
	'''
	name=serializers.CharField(max_length=60,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.department_id=int(kwargs.pop('department_id',0))
		super(DivisionSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		

		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorHRDivisionNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now. Make sure the department exists first



				if self.department_id<=0:
					errmsg['department']=_('ErrorHRDivisionInvalidDepartment')
				else:
					try:
						department=Department.objects.get(pk=self.department_id)

						#department is ok. Ensure the name of the division is unique within the Head now
						ensure_unique={}
						
						if self.current_row_id>0:
							ensure_unique['id']=self.current_row_id
							ensure_unique['department_id']=self.department_id

						if Division.objects.filter(name=name,department_id=self.department_id).exclude(**ensure_unique).exists():
							errmsg['name']=_('ErrorHRDivisionNameExists') % {'division_name':name,'dept_name':department.name}

					except:
						errmsg['department']=_('ErrorHRDivisionInvalidDepartment')

		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		

		return data



class UnitSerializer(serializers.Serializer):
	'''
	Make sure Unit information is ok before you save it
	'''
	name=serializers.CharField(max_length=60,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	

	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		self.division_id=int(kwargs.pop('division_id',0))
		super(UnitSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		

		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorHRUnitNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now. Make sure the division exists first

				if self.division_id<=0:
					errmsg['division']=_('ErrorHRUnitInvalidDivision')
				else:
					try:
						division=Division.objects.get(pk=self.division_id)

						#division is ok. Ensure the name of the unit is unique within the Division now
						ensure_unique={}
						
						if self.current_row_id>0:
							ensure_unique['id']=self.current_row_id
							ensure_unique['division_id']=self.division_id

						if Unit.objects.filter(name=name,division_id=self.division_id).exclude(**ensure_unique).exists():
							errmsg['name']=_('ErrorHRUnitNameExists') % {'unit_name':name,'division_name':division.name}

					except:
						errmsg['department']=_('ErrorHRUnitInvalidDivision')

		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')


		if errmsg:
			raise serializers.ValidationError(errmsg)

		return data


class ProfessionSerializer(serializers.Serializer):
	'''
	Make sure Profession information is ok before you save it
	'''
	name=serializers.CharField(max_length=60,allow_blank=False,required=True)
	active=serializers.IntegerField(required=True)
	
	def __init__(self,*args,**kwargs):
	
		self.current_row_id=int(kwargs.pop('current_id', 0))
		super(ProfessionSerializer, self).__init__(*args, **kwargs)

	def validate(self,data):
		#validate the data here
	
		
		name=data.get('name','').strip()
		active=data.get('active','2')
		
		errmsg={}

		if len(name)<3:
			errmsg['name']=_('ErrorHRProfessionNameShort') % {'min': '3'}
		else:
			#make sure it does not contain invalid characters
			check_invalid_characters=validateCharacters(name, _('Name'))
			if check_invalid_characters:
				errmsg['name']=check_invalid_characters

			else:
				#make sure it is unique now
				ensure_unique={}
				if self.current_row_id>0:
					ensure_unique['id']=self.current_row_id

				if Profession.objects.filter(name=name).exclude(**ensure_unique).exists():
					errmsg['name']=_('ErrorHRProfessionNameExists')

		if active not in [1,0]:
			errmsg['active']=_('ErrorGenericInvalidActiveState')

		if errmsg:
			raise serializers.ValidationError(errmsg)

		return data