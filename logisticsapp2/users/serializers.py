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
from hr.models import Department, Division, Employee, Head, Office, Profession, Unit
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from validation.validators import validateCharacters

from tools.usergroups import DefaultUserGroups

from tools.checkup import emailIsUnique,checkEmailFormat
from datetime import date,timedelta #for checking renewal date range.










class EmployeeSerializer(serializers.Serializer):
	'''
	Make sure employee information is correct
	'''
	first_name=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	last_name=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	gender=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	title=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	phone=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	idcard=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	rlrc_id=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	email=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30) #

	head=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	dept=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30) #
	division=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)
	unit=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	office=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#
	job=serializers.CharField(allow_blank=True,allow_null=True,required=False,max_length=30)#



	def __init__(self,*args,**kwargs):
		self.current_user_id=int(kwargs.pop('user_id', 0))
		super(EmployeeSerializer, self).__init__(*args, **kwargs)






	

	def validate(self,data):
		#validate the data here

		errmsg={}

		exclude={} #used during editing only

		#1. Do we have employees user group?
		user_roles=DefaultUserGroups()
		employee_role=user_roles.default()

		if employee_role==None:
			errmsg['name']=(_('ErrorRegisterUserEmployeeGroupMissing'))
		else:
			#we can check other data now
			first_name=data.get('first_name','').strip().capitalize()
			last_name=data.get('last_name','').strip().capitalize()
			gender=data.get('gender','').strip().capitalize()
			title=data.get('title','').strip().capitalize()
			phone=data.get('phone','').strip()
			
			idcard=data.get('idcard','')
			
			email=data.get('email','').strip()
			
			head=data.get('head','')
			dept=data.get('dept','')
			division=data.get('division','')
			unit=data.get('unit','')
			office=data.get('office','')
			job=data.get('job','').strip()

			rlrc_id=data.get('rlrc_id','')

			if len(first_name)<3:
				errmsg['first_name']=_('ErrorEmpRegisterFirstNameTooShort') % {'min': '3'}
			else:
				#make sure it does not contain invalid characters
				check_invalid_characters=validateCharacters(first_name, _('Name'))
				if check_invalid_characters:
					errmsg['first_name']=check_invalid_characters
			

			if not title:
				errmsg['title']=_('ErrorEmpRegisterInvalidTitle')

			
			
				


			if len(last_name)<3:
				errmsg['last_name']=_('ErrorEmpRegisterLastNameTooShort') % {'min': '3'}
			else:
				#make sure it does not contain invalid characters
				check_invalid_characters=validateCharacters(last_name, _('Name'))
				if check_invalid_characters:
					errmsg['last_name']=check_invalid_characters

			#confirm email: must be valid and unique

			if not checkEmailFormat(email,required=True):
				errmsg['email']=_('ErrorEmpRegisterInvalidEmail')
			else:
				#is it unique?
				if not emailIsUnique(email,self.current_user_id):
					errmsg['email']=_('ErrorEmpRegisterEmailExists')


			genders=[x[0] for x in Employee.GENDER]

			if gender not in genders:
				errmsg['gender']=_('ErrorEmpRegisterInvalidGender')


			if self.current_user_id>0:
				exclude['user_id']=self.current_user_id



			if idcard!=None:
				if len(idcard)==16:
					idcard=idcard.strip()
					if Employee.objects.filter(idcard=idcard).exclude(**exclude).exists():
						errmsg['idcard']=_('ErrorEmpRegisterIDCardExists') % {'idcard':idcard}
				else:
					data['idcard']=None

			else:
				data['idcard']=None

				 
					


			#check phone number now. It should contain just digits and be 10 digits long: 07 83 81 27 06. It should start with 07
			
			if len(phone)!=10 or not phone.isdigit():
				errmsg['phone']=_('ErrorEmpRegisterPhoneNumberShort') % {'exact':'10'}
			else:
				#make sure it is unique
				if Employee.objects.filter(phone=phone).exclude(**exclude).exists():
					errmsg['phone']=_('ErrorEmpRegisterPhoneNumberExists')

			#check rlrc_id. Please fix the way this check is happening. RLRC Employee ID is expected to have a proper format and fixed length

			if rlrc_id!=None:
				rlrc_id=rlrc_id.strip()
				if len(rlrc_id)>0:
					if Employee.objects.filter(rlrc_id=rlrc_id).exclude(**exclude).exists():
						errmsg['rlrc']=_('ErrorEmpRegisterRLRCIDExists')

	

			

			#confirm job placement here. We start checking by Unit.

			if self.current_user_id==0:

				hr_kind=None
				hr_id=0

				try:
					office=int(office)
					if office>0:
						if not Office.objects.filter(pk=office).exists():
							errmsg['office']=_('ErrorEmpRegisterInvalidOffice')
						else:
							hr_kind='office'
							hr_id=office
				except:
					office=0

				if office==0:

					try:
						unit=int(unit)
						if unit>0:
							#selected a unit. So employement is in happening in Unit level of the HR
							if not Unit.objects.filter(pk=unit,active=1).exists():
								errmsg['unit']=_('ErrorEmpRegisterHRInvalidUnit')
							else:
								hr_kind='unit'
								hr_id=unit


					except:
						unit=0

				if unit==0:
					#he didnt select a unit. Ddid he may be selected division?
					try:
						division=int(division)

						if division>0:
							if not Division.objects.filter(pk=division,active=1).exists():
								errmsg['division']=_('ErrorEmpRegisterHRInvalidDivision')
							else:
								hr_kind='division'
								hr_id=division
								

					except:

						division=0

					#should we check department?
					if division==0:
						try:
							dept=int(dept)
							if dept>0:
								if not Department.objects.filter(pk=dept,active=1).exists():
									errmsg['dept']=_('ErrorEmpRegisterHRInvalidDept')
								else:
									hr_kind='dept'
									hr_id=dept
						except:
							dept=0

						#should we check head?
						if dept==0:
							try:
								head=int(head)
								if head>0:
									if not Head.objects.filter(pk=head,active=1).exists():
										errmsg['head']=_('ErrorEmpRegisterHRInvalidHead')
									else:
										hr_kind='head'
										hr_id=head

							except:
								head=0

				#job
				try:
					job=int(job)
				
					if job>0:
						if not Profession.objects.filter(pk=job,active=1).exists():
							errmsg['job']=_('ErrorEmpRegisterHRInvalidJob')
					else:
						errmsg['job']=_('ErrorEmpRegisterHRInvalidJob')


				except:
					job=0


				if hr_kind==None:
					errmsg['hr']=_('ErrorEmpRegistrationHRMissing')






		if errmsg:
			raise serializers.ValidationError(errmsg)

	

		if self.current_user_id==0:
		
			data['hr_kind']=hr_kind
			data['hr_id']=hr_id

		return data