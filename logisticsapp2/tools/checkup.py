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
from django.core.validators import validate_email
from django.contrib.auth.models import User



def emailIsUnique(email,user_id=0):
	'''
	Is the email unique? if user_id>0, then exclude checking if the email belongs to the user and see if any other remaining users have the email?

	return boolean. True if exists, else false
	'''

	exclude={}

	if user_id>0:
		exclude['id']=user_id
	
	#we got username so its invalid
	if User.objects.filter(email=email).exclude(**exclude).exists():
		return False
	else:
		return True




def checkPhone(phone):
	'''
	Checks if lenght of phone is minimum 9 and 13 length. Note hte best of its kind and definitely needs rewriting but will work
	well for the purose of the application on its current client
	
	return boolean;true if valid, false if not.
	'''
	
	try:
		if phone.isdigit():
			minlen=9
			maxlen=13
			phone=str(phone)
			if len(phone)<minlen or len(phone)>maxlen:
				return False
			else:
				return True
	except BaseException as e:
		return False


def checkEmailFormat(email,required=True):
	'''
	Check if the email is in valid format (abc@example.com)

	if required=True, then if the email is not given (i.e. null or empty), then return false. If it is not required and is empty, return true
	'''


	if not email and not required:
		#the email field is not given but is also not required so return true.
		return True

	try:
		validate_email(email)
		return True
	except:
		return False






