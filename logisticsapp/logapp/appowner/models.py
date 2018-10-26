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
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group


# Create your models here.

class Information(models.Model):
	code=models.PositiveIntegerField(default=1005,primary_key=True)
	name=models.CharField(max_length=100,default='Law Reform Commission')
	productname=models.CharField(max_length=255,default='Logistics')
	tele=models.CharField(max_length=18)
	fax=models.CharField(max_length=18,null=True,blank=True)
	www=models.URLField(max_length=255)
	email=models.EmailField(max_length=50)
	address=models.TextField()
	#logo=models.CharFieldField(null=True,blank=True,upload_to = 'static/logo/', default = 'static/logo/logo.png',validators=[validateLogo])
	history=models.TextField(null=True,blank=True)
	createdon=models.DateTimeField(auto_now_add=True)
	updatedon=models.DateTimeField(auto_now=True)
	idcode=models.CharField(max_length=3,default='LRC')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _('InstitutionInformation')
		verbose_name_plural = _('InstitutionInformation')



class Configuration(models.Model):
	'''
	Configuration set forth by the app owner. Might be linked to settings.py
	'''
	OPTIONS=((1,_('Yes')), (0,_('No')))
	code=models.PositiveIntegerField(default=1001,primary_key=True)
	enable_emailing=models.PositiveIntegerField(default=1,choices=OPTIONS)
	auto_activate_users=models.PositiveIntegerField(default=0,choices=OPTIONS)

	def __str__(self):
		return str(_('Configuration'))


	class Meta:
		verbose_name = _('Configuration')
		verbose_name_plural = _('Configuration')


class DefaultUserGroup(models.Model):
	'''
	Default user group where newly created users will be added to
	'''
	group=models.OneToOneField(Group)

	def __str__(self):
		return self.group.name
