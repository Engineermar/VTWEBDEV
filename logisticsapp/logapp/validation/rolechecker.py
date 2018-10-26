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

from django.contrib.auth.models import User

from oauth2_provider.models import Application
from django.contrib.auth.models import Permission


def validApplication(client_id,client_secret='',client_secret_must=True):
	'''
	is the application making the call valid or not? Since multiple applications can be defined (Web App, Mobile App, USSD App etc), we want to valid
	if the client_id,client_secret exist in teh system

	@input: client_id defined by the admin. Required
			client_secret: defined by the admin. Optional
			client_secret_must: boolean. If True, client_secret is required. If not, just check client_id

	@output: boolean. True if valid else False
	'''
	reply=False #assume it is invalid and shouldnt access the system
	goon=True

	try:
		filters={'client_id':client_id}
		if client_secret_must:
			if client_secret:
				filters['client_secret']=client_secret
			else:
				goon=False

		if goon:
			app=Application.objects.get(**filters)
			reply=app.name

	except:
		reply=False




	return reply 




def userIsPermittedTo(user_id,needed_permissions=[]):
	'''
	Does the user have the given permission? Ths is a decorator in its own right but not implemented as one due to the localization difficulty with Tigriniyia (Django Replying its own messages as Not Permitted)

	On to do list to be rewritten as a decorater with localization support for error message when permission is not found

	@input: user_id the id of hte user whose permirmission is to be checked
			needed_permissions: an array of permissions that needed to be checked

	@output: True if any of the permissions are found ; else False

	Note: permissions are checked on individually assigned or grooup assigned

	'''
	reply=False
	user=User.objects.get(pk=user_id)
	
	my_permissions=user.user_permissions.filter(codename__in=needed_permissions).values_list('codename',flat=True) | Permission.objects.filter(group__user=user,codename__in=needed_permissions).values_list('codename',flat=True)
	if my_permissions:
		reply=True

	return reply

	#groups=list(User.objects.get(pk=user_id).groups.values_list('id',flat=True))

	#reply=Permission.objects.filter(group__in=groups,codename__in=needed_permissions).exists()

	








