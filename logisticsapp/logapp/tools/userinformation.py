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

from hr.models import Employee


def preferences(userid,lookfor=['lang',]):
	'''
	Get the preference of the user.
	@input: userid =>the id of hte user whose preferences we want to get
			lookfor=>an array of Model fields we want to get. If not provded, language is of the user is returned
	@ouptut: None or the preference object
	'''
	
	choices=None
	try:
		choices=Employee.objects.values(lookfor).get(user_id=userid)
	except:
		choices=None

	return choices



