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
from datetime import date,datetime
import string
import random
from tools.company import productInformation
from app.conf import base as settings
import uuid
import hashlib

def generateInvoiceCode(kind='IN'):
	today=datetime.now(settings.PYTZ_CONST)
	dt=''.join(  [str(today.minute), str(today.year), str(today.day),  str(today.month), str(today.second), str(today.hour)])
	rands=''.join(random.choice(string.digits ) for _ in range(5))

	return ''.join([kind,rands, dt ])


def generateProductTag(invoiceid,asset_code):
	'''
	CREATE A TAG FOR NON-CONSUAMBLE ASSETS.
	'''
	if asset_code==None:
		asset_code=''
	today=datetime.now(settings.PYTZ_CONST)
	dt=''.join(  [str(today.minute), str(today.year), str(today.day),  str(today.month), str(today.second), str(today.hour)])

	rand=''.join(random.choice(string.digits ) for _ in range(5))

	code=''.join([dt , str(rand) , str(invoiceid)])
	#encrypt the code first
	new_code=int(hashlib.sha256(code.encode('utf-8')).hexdigest(), 16) % 10**15 #8 digits

	new_code=''.join([asset_code, str(new_code)])

	return new_code


def generateProcessingBatchCode(id,call):
	'''
	this can be used from various zones. E.g. when adding new items, items that were added at once are called one batch. The code is barely 
	used outside visually and is purely for internal operations
	'''
	today=datetime.now(settings.PYTZ_CONST)
	dt=''.join(  [str(today.minute), str(today.year), str(today.day),  str(today.month), str(today.second), str(today.hour)])

	rand=''.join(random.choice(string.digits ) for _ in range(15))

	code=''.join([dt , str(rand) , str(id)])
	#encrypt the code first
	new_code=hashlib.sha256(code.encode('utf-8')).hexdigest()

	new_code=''.join([call  , '-' , str(new_code)])

	return new_code	



















	

def generateChangeEmailToken(user_id):
	'''
	When user wants to change his/her email, send him a link with the following token

	Or when registerering, create a new activate link.

	'''
	salt = uuid.uuid4().hex
	dt=datetime.now(settings.PYTZ_CONST)
	token=hashlib.sha256(salt.encode() + str(user_id).encode() + str(dt).encode()).hexdigest()
	return token





def generateResetPasswordToken():
	'''
	When user forgots his/her password, we generate a unique token for the request.

	'''
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(102))


def generateRandomPassword():
	'''
	Generate a password for the given value
	'''
	pwd=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
	return pwd









def generateEmployeeCompanyID():
	'''
	Generate member ID

	'''
	
	try:
		product_information=productInformation()
		company_code=product_information['company_idcode']
		now=str(date.today().month)+str(date.today().year)
		random_to_generate=16-len(company_code+now)
		random_numbers=''.join(random.choice(string.digits) for _ in range(4))
		randomChars=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random_to_generate))
		return ''.join([company_code,random_numbers,now,randomChars])

	
	except BaseException as e:
		return ''

	
