from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import app.appsettings as appsettings


class Employee(models.Model):
	'''
	Stores list of employees
	'''
	GENDER=(('M','M'),('F','F'))
	
	title=models.CharField(max_length=10)
	user=models.OneToOneField(User,related_name='user_employee',on_delete=models.CASCADE)
	gender=models.CharField(max_length=1,choices=GENDER)
	phone=models.CharField(max_length=13)
	idcard=models.CharField(max_length=16,null=True,blank=True)
	rlrc_id=models.CharField(max_length=30,null=True,blank=True)
	company_id=models.CharField(max_length=30,unique=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='admin_employee')
	registered_via=models.CharField(max_length=30)
	status=models.PositiveIntegerField(default=1) #1 unblocked; 0=blocked

	def __str__(self):
		return self.phone

	






class Head(models.Model):
	'''
	In organizational structure, the Head is the top. E.g. Administration.
	'''
	name=models.CharField(max_length=60,unique=True)
	
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	active=models.PositiveIntegerField(default=1)
	added_by=models.ForeignKey(User,related_name='admin_head')


class Department(models.Model):
	'''
	In org structure, department is a child of a head. E.g. the Head Administration might have dept of admin,finance etc under it
	'''
	name=models.CharField(max_length=60)
	head=models.ForeignKey(Head,related_name='head_dept')
	
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	active=models.PositiveIntegerField(default=1)
	added_by=models.ForeignKey(User,related_name='admin_department')

	class Meta:
		unique_together=('head','name')


class Division(models.Model):
	'''
	Division comes under Department.
	'''
	name=models.CharField(max_length=60)
	department=models.ForeignKey(Department,related_name='division_dept')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	active=models.PositiveIntegerField(default=1)
	added_by=models.ForeignKey(User,related_name='admin_division')

	class Meta:
		unique_together=('name','department')


class Unit(models.Model):
	'''
	Unit is the actual place an employee is assigned for.A unit comes under a division.
	'''
	name=models.CharField(max_length=60,unique=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	active=models.PositiveIntegerField(default=1)
	division=models.ForeignKey(Division,related_name='division_unit')
	added_by=models.ForeignKey(User,related_name='admin_unit')


class Profession(models.Model):
	'''
	list of possible jobs an employee can have in the company
	'''
	name=models.CharField(max_length=70,unique=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	active=models.PositiveIntegerField(default=1)
	added_by=models.ForeignKey(User,related_name='admin_profession')


class Office(models.Model):
	'''
	Each Head, dept,div or unit has an office. here we list of those offices each in one.
	'''
	head=models.ForeignKey(Head,related_name='office_head',default=None,db_index=True,null=True)
	dept=models.ForeignKey(Department,related_name='office_dept',default=None,db_index=True,null=True)
	division=models.ForeignKey(Division,related_name='office_division',default=None,db_index=True,null=True)
	unit=models.ForeignKey(Unit,related_name='office_unit',default=None,db_index=True,null=True)
	name=models.CharField(max_length=70)

	def __str__(self):
		return self.name




class EmployeePosition(models.Model):
	'''
	Employee position in the company. an employee can work in any of the above places. Hence, the relationship will be loose kind with each with index and null
	'''
	employee=models.ForeignKey(Employee,related_name='position_emp',on_delete=models.CASCADE)
	unit=models.ForeignKey(Unit,related_name='position_unit',on_delete=models.PROTECT,db_index=True,null=True,blank=True)
	office=models.ForeignKey(Office,related_name='position_office',on_delete=models.PROTECT,db_index=True,null=True,blank=True)
	division=models.ForeignKey(Division,related_name='position_division',on_delete=models.PROTECT,db_index=True,null=True,blank=True)
	department=models.ForeignKey(Department,related_name='position_department',on_delete=models.PROTECT,db_index=True,null=True,blank=True)
	head=models.ForeignKey(Head,related_name='position_head',on_delete=models.PROTECT,db_index=True,null=True,blank=True)
	job=models.ForeignKey(Profession,related_name='position_profession',on_delete=models.PROTECT)
	active=models.PositiveIntegerField(default=1)
	quit_on=models.DateField(null=True,blank=True,default=None)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	added_by=models.ForeignKey(User,related_name='admin_emp_position')


class Message(models.Model):
	'''
	Message sent to a particular employee. The message could be long or short in any language. It can come from the system automatically,be sent to email
	'''
	employee=models.ForeignKey(Employee,related_name='employee_message')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	subject=models.CharField(max_length=200)
	content=models.CharField(max_length=10000)
	sender=models.ForeignKey(Employee,related_name='sender_message',db_index=True,null=True,blank=True,default=None)
	is_read=models.IntegerField(default=0)
	delete_from_inbox=models.IntegerField(default=0)
	delete_from_sent=models.IntegerField(default=0)


class PasswordReset(models.Model):
	profile=models.ForeignKey(User,related_name='user_pwdreset')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	unique_code=models.CharField(max_length=255)


class EmailChangeVerifications(models.Model):
	profile=models.ForeignKey(User,related_name='user_changeemail')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	unique_code=models.CharField(max_length=255)
	email=models.EmailField(max_length=25)

class AccountVerification(models.Model):
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	unique_code=models.CharField(max_length=255)
	email=models.EmailField(max_length=25)

class Notification(models.Model):
	'''
	Notifications created by a particular action. user creates the notification
	'''
	NOTIFY_KIND=(('1',_('NotifyKindHRChanged')), ('2',_('NotifyKindCataglogChanged')))
	user=models.ForeignKey(User,related_name='user_notification',on_delete=models.CASCADE)
	addedon=models.DateField()
	notify_kind=models.CharField(choices=NOTIFY_KIND,max_length=3)
	content=models.CharField(max_length=300,null=True,blank=True)
	link=models.CharField(max_length=1000,null=True,blank=True)
	is_counted=models.IntegerField(default=0)


class SupportRequest(models.Model):
	'''
	This is viewable by employees who have admin powers only. Employee refers to the employee who requested password assistance.
	'''
	KIND=(('Change Email',_('ChangeEmail')), (('Change Password'),_('ChangePwd'))  )
	employee=models.ForeignKey(Employee,related_name='employee_pwdresetrequest')
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	kind=models.CharField(choices=KIND,max_length=25)
	message=models.CharField(max_length=10000,null=True,blank=True)




