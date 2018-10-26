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
from appowner.models import Information

def productInformation():
	'''
	Return the product information in the form of a dictionary:

	company_name:....
	product_name:....
	company_idcode:....

	The calling function or module might not need all the three information but it doesn't affect the query so.
	'''

	reply={'company_name':'','product_name':'','company_idcode':''}

	try:
		info=Information.objects.values('name','productname','idcode').get()
		reply['company_name']=info['name']
		reply['product_name']=info['productname']
		reply['company_idcode']=info['idcode']
	except:
		pass

	return reply
