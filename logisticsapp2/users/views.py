from app.conf import base as settings
from tools.formtools import createErrorDataJSON,csvFromUrlToNumbers
from datetime import date
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse
from django.contrib.auth.models import User,Group


from hr.models import AccountVerification, Department, Division, Employee, EmployeePosition, Head, Profession, Unit

from django.utils.translation import ugettext_lazy as _

from validation.rolechecker import userIsPermittedTo

from logistic.models import IncomingInvoice,OutgoingInvoice,ReturnItemInvoice,ItemInStore,IncomingItem,Provider

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import app.appsettings as appsettings


from tools.build_quries import searchUserByNameQueryBuilder
from django.db.models import Q

from tools.tokens import deleteUserToken
from tools.generators import generateRandomPassword,generateEmployeeCompanyID,generateChangeEmailToken
from mailer.simplemail import emailResetPasswordMessage,emailRegistrationDetails
from django.contrib.auth.models import Group

from users.serializers import EmployeeSerializer

from tools.usergroups import DefaultUserGroups
from tools.readconfiuration import readConfiguration



class ListProgramUsers(APIView):
	'''
	List of program users, which could include any/user.

	Output can be paginated or not, based on request
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_view_users'])


		if have_right==True:
			#return list of users with powers now. Note that we can have them filtered with query parameters

			needed_roles=request.query_params.get('roles','')
			active=request.query_params.get('active',-1)
			needed_roles=csvFromUrlToNumbers(needed_roles,num='str')
			search_option=request.query_params.get('search_option','').strip().lower()
			search_value=request.query_params.get('search_value','').strip()
			pagenate_me=request.query_params.get('paginated','1').strip()

			if pagenate_me not in ['0','1']:
				pagenate_me=1 #default paginate
			

			filters={}

			try:
				active=int(active)
				if active in [0,1]:
					filters['user__is_active']=active

			except:
				pass



			if search_value:

				if search_option=='email':
					filters['user__email__icontains']=search_value
				elif search_option=='phone':
					filters['phone']=search_value

				elif search_option=='empid':
					filters['company_id']=search_value
				elif search_option=='idcard' and len(search_value)>6:
					filters['idcard__icontains']=search_value
				elif search_option=='username':
					filters['user__username__icontains']=search_value
				elif search_option=='name':
					name_filters=searchUserByNameQueryBuilder(search_value)
					if name_filters:
						for k in name_filters:
							filters[k]=name_filters[k]

		


			

			if needed_roles:
				filters['user__groups__name__in']=needed_roles

			employees=Employee.objects.filter(**filters).values('id','user_id','user__first_name','user__last_name','gender','title','company_id','user__is_active','status','phone','user__email').order_by('user__first_name','user__last_name')
			
			if pagenate_me=='1':

				p=request.query_params.get('page')
				
				try:
					
					page=request.query_params.get('page',1)

					paginator=Paginator(employees,appsettings.APPSET_NUMBER_OF_USERS_TO_SHOW)
					data=paginator.page(page)
					status=200
				except PageNotAnInteger:
					data=paginator.page(1)
					status=200
				except EmptyPage:
					data=paginator.page(paginator.num_pages)
					status=200

				except:
					data=None
					status=400
					reply['detail']=(_('InvalidPath'))

				if status==200:
					reply['detail']=list(data)
					reply['total_num_of_pages']=paginator.num_pages
					reply['total_rows_found']=paginator.count
					reply['total_per_page_allowed']=appsettings.APPSET_NUMBER_OF_USERS_TO_SHOW
					reply['current_page']=page

			else:
				#not paginated
				reply['detail']=list(employees)	
				status=200

		
		else:
			reply['detail']=_('NoRight')

		return JsonResponse(reply,status=status)


class MyHRInformation(APIView):
	'''
	Return departments etc I currently work in. This is my CURRENT user him/erself, used notably wen requesting items
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		#since log is all we care about here, we dont check for rights.

		reply={}
		active=request.query_params.get('active','1')
		if active.capitalize() not in ['1','0']:
			active=1
		reply['detail']=list(EmployeePosition.objects.filter(employee__user_id=request.user.id,active=active).values('head__name','department__name','division__name','unit__name','employee_id', 'department_id','head_id','unit_id','division_id','office_id','office__name'))
		employee=Employee.objects.get(user_id=request.user.id)
		reply['employee_id']=employee.id
		return JsonResponse(reply,status=200)



class EmployeePositions(APIView):
	'''
	Return positions of the given employee, who must exist first.Accept user _id of the employee
	'''

	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,emp_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_view_positions'])
		if have_right==True:

			#does the employee exist?

			try:
				user=User.objects.values('id','first_name','last_name','email','user_employee__phone','user_employee__id','is_active','user_employee__status','user_employee__company_id','user_employee__idcard').get(pk=emp_id)
				#user does exist. Now return the positions of the employee
				reply['user']=user

				reply['positions']=list(EmployeePosition.objects.filter(employee__user_id=emp_id).values('id','head__name','department__name','division__name','unit__name','job__name','active','office__name','quit_on','createdon','added_by__first_name','added_by__last_name'))
				status=200
			except:
				reply['detail']=_('ErrorUserMissing')

		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class EmployeeFromPosition(APIView):
	'''
	Accept position id of an employee and get the information.
	'''
	def get(self,request,position_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_view_positions'])
		if have_right==True:

			try:
				reply['detail']=EmployeePosition.objects.values('employee__user__first_name','employee__user__last_name','employee__user__email','employee__phone','active','head__name','department__name','division__name','unit__name','job__name').get(pk=position_id)
				status=200
			except:
				reply['detail']=_('ErrorEmployementPositionNotFound')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)	


class EmployeesWorkingIn(APIView):
	'''
	View employees working in a specific place i.g. Head,Dept etc. Show current employees only

	kind=>h,d,v,u
	kind_id=>id of the above.
	'''
	def get(self,request,kind,kind_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_view_manage_hr'])
		if have_right==True:

			filters={'active':1}

			if kind=='h':
				filters['head_id']=kind_id

			elif kind=='d':
				filters['department_id']=kind_id

			elif kind=='v':
				filters['division_id']=kind_id

			elif kind=='u':
				filters['unit_id']=kind_id


			if filters:
				reply['detail']=list(EmployeePosition.objects.filter(**filters).values('id','employee__user__first_name','employee__user__last_name','employee__user__email','employee__phone','job__name','employee_id','employee__user_id').order_by('employee__user__first_name','employee__user__last_name'))
				status=200

			else:
				reply['detail']=_('InvalidPath')
			


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class DeleteUser(APIView):
	'''
	delete a given user. Note that deletion can happen only i hte user is clear of everything.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_user'])
		if have_right==True:
			user_id=request.data.get('user_id',0) #

			#purify user.
			#did user register any IncomingInvoice or Got some? IncomingInvoice,OutgoingInvoice,ReturnItemInvoice
			if Provider.objects.filter(processedby_id=user_id).exists():
				reply['detail']=_('ErrorUserDeletionDepedencyProvider')
			else:
				if ItemInStore.objects.filter(processedby_id=user_id).exists():
					reply['detail']=_('ErrorUserDeletionDepedencyInStoreItems')
				
					if IncomingInvoice.objects.filter(processedby_id=user_id).exists():
						reply['detail']=_('ErrorUserDeletionDepedencyIncomingInvoice')
					else:
						if IncomingItem.objects.filter(processedby_id=user_id).exists():
							reply['detail']=_('ErrorUserDeletionDependencyIncomingItem')
						else:
							if OutgoingInvoice.objects.filter(Q(processedby__id=user_id) | Q(give_to__employee__user_id=user_id)).exists():
								reply['detail']=_('ErrorUserDeletionDependencyOutgoingInvoice')
							else:
								if ReturnItemInvoice.objects.filter(Q(processedby_id=user_id) | Q(return_by__employee__user_id=user_id)).exists():
									reply['detail']=_('ErrorUserDeletionDependencyReturnInvoice')


			#should we check User in HR module?

			if reply.get('detail','')=='':
				#purify HR modules as well.
				if Employee.objects.filter(added_by_id=user_id).exists():
					reply['detail']=_('ErrorUserDeletionDependencyRegEmployee')
				else:
					if Head.objects.filter(added_by_id=user_id).exists():
						
						reply['detail']=_('ErrorUserDeletionDependencyOrgStructure')
					else:
						if Department.objects.filter(added_by_id=user_id).exists():
							
							reply['detail']=_('ErrorUserDeletionDependencyOrgStructure')
						else:
							if Division.objects.filter(added_by_id=user_id).exists():
								
								reply['detail']=_('ErrorUserDeletionDependencyOrgStructure')
							else:
								if Unit.objects.filter(added_by_id=user_id).exists():
									
									reply['detail']=_('ErrorUserDeletionDependencyOrgStructure')
								else:
									if Profession.objects.filter(added_by_id=user_id).exists():
										
										reply['detail']=_('ErrorUserDeletionDependencyOrgStructure')

		

			#do we have error now or not?
			if reply.get('detail','')=='':
				#no error. hence get the user to delete him. first tho, delete him from employees table.
				try:

					user=User.objects.get(pk=user_id)

					employee=Employee.objects.get(user_id=user_id)

					positions=EmployeePosition.objects.filter(employee_id=employee.id)

					positions.delete()

					employee.delete()

					user.delete()
					status=200
					reply['detail']=_('UserDeleted')
				except:

					reply['detail']=_('ErrorUserDeleteMissing')


		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class DeletePosition(APIView):
	'''
	delete position of an employee.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['delete_employeeposition'])
		if have_right==True:
			user_id=request.data.get('user_id',0) #
			position_id=request.data.get('pos_id',0)

			try:
				position=EmployeePosition.objects.get(employee__user_id=user_id,pk=position_id)
				position.delete()
				status=200
				reply['detail']=_('PositionDeletedSuccessfully')
			except:
				reply['detail']=_('ErrorDeletePositionMissing')

	
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class ActivateDeactivatePosition(APIView):
	'''
	activate or deactivate position of an employee. Here, we toggle the active state of the position
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['change_employeeposition'])
		if have_right==True:
			user_id=request.data.get('user_id',0) #
			position_id=request.data.get('pos_id',0)
			
			try:
				position=EmployeePosition.objects.get(employee__user_id=user_id,pk=position_id)
				if position.active==1:
					position.quit_on=date.today()
					reply['new_status']=0
					position.active=0
				else:
					position.quit_on=None
					position.active=1
					reply['new_status']=1

				position.save()
				status=200
				reply['detail']=_('PositionUpdateOk')
			
			except:
				reply['detail']=_('PositionUpdateError')
	
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class StripRoles(APIView):
	'''
	Strip roles of hte user except 'employees' or the default function
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		user_roles=DefaultUserGroups()
		employee_role=user_roles.default()
		exclude={}
		if employee_role!=None:
			exclude['id']=employee_role.id

		have_right=userIsPermittedTo(request.user.id,['can_strip_user_roles'])

		if have_right:
			user_id=request.data.get('user_id',0)
			try:
				user=User.objects.get(pk=user_id)
				groups=list(user.groups.all().exclude(**exclude).values('id',))
				
				if groups:
					for g in groups:
						print(g)
						user.groups.remove(g['id'])
					status=200
					reply['detail']=_('RolesStripOK')
				else:
					reply['detail']=_('ErrorUserStripAllRolesNoneFound')
			except:
				reply['detail']=_('ErrorUserStripGroupNotMissing')
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class ActivateDeactivateUser(APIView):
	'''
	Deactivate or deactivate a user. This toogles the state.
	'''

	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_act_deact_user'])

		if have_right:
			user_id=request.data.get('user_id',0)
			try:
				user=User.objects.get(pk=user_id)
				current_state=user.is_active
				new_status=1
				reply['detail']=_('UserActivatedOk')
				if current_state==1:
					reply['detail']=_('UserDeactivatedOk')
					new_status=0

				user.is_active=new_status
				user.save()
				#if deactivated, delete token
				if new_status==0:
					deleteUserToken(user_id)

				reply['new_status']=new_status
				status=200
				
			except:
				reply['detail']=_('ErrorUserMissing')
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class UserResetPassword(APIView):
	'''
	Reset password of a given user
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['extra_reset_userpassword'])

		send_email=False

		if have_right:
			user_id=request.data.get('user_id',0)

			try:
				user=User.objects.get(pk=user_id)
				#generate a random password
				new_pwd=generateRandomPassword()
				user.set_password(new_pwd)
				user.save()
				#email
				reply['detail']=_('UserPasswordResetted') % {'email': user.email}
				
				status=200
				send_email=True
				
			except:
				reply['detail']=_('ErrorUserMissing')


			if send_email:
				#try sending the email now
				try:
					emailResetPasswordMessage(settings.LANGUAGE_CODE,user.email,user.username,user.first_name,new_pwd)
				except:
					status=400
					reply['detail']=_('ErrorEmailingUserPassword')

			



		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)



class UserRoles(APIView):
	'''
	List of roles for a specific user. Accessible to Manager only
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,user_id,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_view_user_rights'])

		if have_right:
			
			try:
				user=User.objects.get(pk=user_id)
				reply['full_name']=' '.join([user.user_employee.title,user.first_name,user.last_name])
				reply['email']=user.email
				reply['phone']=user.user_employee.phone
				reply['company_id']=user.user_employee.company_id
				reply['my_roles']=list(User.objects.filter(pk=user_id).values_list('groups__name',flat=True))
				reply['groups']=list(Group.objects.all().values('name',))

				status=200
				
			except:
				reply['detail']=_('ErrorUserMissing')
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class UpdateRoles(APIView):
	'''
	We get list of roles in CSV format and update it. First, we delete existing roles except employees. Then we deal with adding roles
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_update_user_rights'])

		if have_right:
			user_id=request.data.get('user_id',0)
			roles=request.data.get('roles')


			user_found=False
		
			
			try:
				user=User.objects.get(pk=user_id)
				
				allowed_roles=DefaultUserGroups()

				default_role=allowed_roles.default()

				exclude={}
				if default_role!=None:
					exclude['id']=default_role.id
				groups=list(user.groups.all().exclude(**exclude).values('id',))
				
				if groups:
					for g in range(len(groups)):
						user.groups.remove(groups[g]['id'])
				user_found=True
			except:
				reply['detail']=_('ErrorUserStripGroupNotMissing')


				
			if user_found:

				
				

				if roles:
					#we have roles
					for role in roles:
						#add them now
						
						if not user.groups.filter(name=role).exists():
							
							try:
								group=Group.objects.get(name=role)
								new_group=user.groups.add(group)
								
							except:
								pass
					
				status=200
				reply['detail']=_('UserEmployeeRolesUpdated')

			
				
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)

class UserRemoveRole(APIView):
	'''
	Strip given role of a person
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_remove_user_right'])

		if have_right:
			user_id=request.data.get('user_id',0)
			role=request.data.get('role','').strip()
			default_role=DefaultUserGroups().default()
			if default_role!=None:
				if default_role.name.lower()==role.lower():
					reply['detail']=_('ErrorUserEmployeeRoleCantRemove')
				else:
					try:

						user=User.objects.get(pk=user_id)
						
						groups=list(user.groups.filter(name=role).values('id',))
						
						if groups:
							for g in range(len(groups)):
								user.groups.remove(groups[g]['id'])
							
							reply['detail']=_('UserRoleDeleted')
						

							status=200
						else:
							reply['detail']=_('ErrorUserRoleRemoveNotFound')
						
					except:
						reply['detail']=_('ErrorUserMissing')

			else:
				reply['detail']=_('ErrorDefaultUserRoleMissing')

				
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class UserAddRole(APIView):
	'''
	Add a new role to a person
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['can_add_user_role'])

		if have_right:
			user_id=request.data.get('user_id',0)
			role=request.data.get('role','').strip()
		
			try:

				user=User.objects.get(pk=user_id)
				
				groups=list(user.groups.filter(name=role).values('id',))
				
				if groups:
					#the group exists already. So reject it
					reply['detail']=_('ErrorUserEmployeeRoleExistsAlready')
				else:
					#add it
					group=Group.objects.get(name=role)
					new_group=user.groups.add(group)
					
					status=200
					reply['detail']=_('UserEmployeeRoleAdded')

				
				
			except:
				reply['detail']=_('ErrorUserorRoleMissing')
			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)


class RegisterNew(APIView):
	'''
	Register new employee/user. Only manager and logistic can register new employee
	'''
	permission_classes = [TokenHasReadWriteScope]

	def post(self,request,format=None):
		reply={}
		status=400

		have_right=userIsPermittedTo(request.user.id,['add_user'])

		email_user=False

		if have_right:
			data=request.data
			serializer=EmployeeSerializer(data=data)
			if serializer.is_valid():
				content=serializer.validated_data
				#generate password for the user':calling_app}
					

				new_pwd=generateRandomPassword()
				position=None #employee position
				profile=None
				user=None

				try:
					#first add to User table
					config=readConfiguration()
					is_active=0
					if config!=None:
						if config.auto_activate_users==1:
							is_active=1


					user=User.objects.create_user(password=new_pwd,first_name=content['first_name'],last_name=content['last_name'],is_superuser=0,username=content['email'],email=content['email'],is_staff=0,is_active=is_active,date_joined=date.today())
					user.save()


					if user:
										
						#Build the Profile Now

						company_id=generateEmployeeCompanyID()
						
						fields={'rlrc_id':content['rlrc_id'],'added_by_id':request.user.id,'company_id':company_id,'phone':content['phone'],'idcard':content['idcard'],'user_id':user.id,'title':content['title'],'gender':content['gender'],'registered_via':request.auth.application.name}

						profile=Employee(**fields)
						profile.save()

						if profile:
							#add him to employees group now
							user_groups=DefaultUserGroups()
							employees=user_groups.default()

							if employees:
								user.groups.add(employees)
							
								


							fields={'added_by_id':request.user.id,'employee_id':profile.id,'job_id':content['job'],'division_id':None,'department_id':None,'head_id':None,'unit_id':None,'active':1,'office_id':None}
							if content['hr_kind']=='unit':
								fields['unit_id']=content['hr_id']
							elif content['hr_kind']=='office':
								fields['office_id']=content['hr_id']
							elif content['hr_kind']=='division':
								fields['division_id']=content['hr_id']
							elif content['hr_kind']=='dept':
								fields['department_id']=content['hr_id']
							else:
								fields['head_id']=content['hr_id']



							position=EmployeePosition(**fields)
							position.save()
							status=200
							reply['detail']=_('UserRegisteredSuccessfully')
							reply['new_id']=user.id
							reply['position_id']=position.id

							if is_active==0:
								email_user=True
							

						else:
							reply['detail']=_('ErrorUserRegistration')
							user.delete()
				

					else:
						reply['detail']=_('ErrorUserRegistration')

				
				except Exception as e:

					status=400
					
					reply['detail']=_('ErrorUserRegistration')
					if position:
						position.delete()

					if profile:
						profile.delete()

					if user:
						user.delete()
				


				#show we go on emailing the user now? We moved it to here to avoid user deletion cos failing to send the email could be a reason to failure leading to account deletion
				if email_user:
					token=generateChangeEmailToken(user.id)
					account=AccountVerification(unique_code=token,email=content['email'])
					account.save()
					try:
						emailRegistrationDetails(token=token,name=content['first_name'],pwd=new_pwd,lang=settings.LANGUAGE_CODE,email=content['email'])
					except:
						if status==200:
							reply['detail']=_('UserRegisteredEmailNotSent')
				
				

			else:
				reply['detail']=createErrorDataJSON(serializer.errors)

			
		else:
			reply['detail']=_('NoRight')


		return JsonResponse(reply,status=status)




class ListUserRights(APIView):
	'''
	List of groups a user can have.
	'''
	permission_classes = [TokenHasReadWriteScope]

	def get(self,request,format=None):
		reply={}
		status=400

		reply['detail']=list(Group.objects.all().values('name','id'))
		status=200
			

		return JsonResponse(reply,status=status)

