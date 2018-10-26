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
#define password rules
from django.utils.translation import ugettext_lazy as _

def confirmPassword(pwd,confirm=None):
	'''
	Make sure the given password is correct or accepted. You can add password complexity check or anything you want here, as required.

	By default, only lenght is checked

	@input: pwd the password to be checked
			confirm if not None, check if it is THE SAME as the pwd arguement. (i.e. matching password confirmation)

	@output: string (error message if an error) or empty string if all is good
	'''
	errmsg=''
	if len(str(pwd))<6 or len(str(pwd))>16:
		errmsg=_('ErrorSecurityPwdLength')
	else:
		if confirm is not None:
			if confirm!=pwd:
				errmsg=_('ErrorSecurityPwdMismatch')

	return errmsg