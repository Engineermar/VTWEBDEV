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
from oauth2_provider.models import AccessToken,RefreshToken
import uuid
import hashlib
from datetime import datetime,timedelta
from app.conf import base as settings
import jwt
import time
from calendar import timegm


def returnMyToken(user_id,app_id):
	'''
	Used during login only. Return a token along with expiration. If unexpired, return the token as it is.

	@input: user_id : the id of the user who wants to get his application token
			app_id: the id of the application the token is attached with

	Remember: a user can have one token per application. So ifthere are four applications defined in Ouath, then a user can have 4 tokens -- one for each app
	'''
	reply={'token':None,'expires':''}


	try:
		token_info=AccessToken.objects.get(user_id=user_id,application_id=app_id)

		token=token_info.token
		expireon=token_info.expires

		#if expired, delete existing tokens.
		dttime=datetime.now(settings.PYTZ_CONST)

		if expireon>=dttime:
			reply['token']=token
			reply['expires']=expireon

	except:
		#doesnt exist
		reply={'token':None,'expires':''}

	return reply
	

def createNewApplicationToken(id,application_id,kind='access'):
	'''
	Generate an application token for the user.

	@input: id the user id
			application_id : if of hte application
			kind: the kind of toekn needed. an access or refresh token
	'''
	expire_seconds=settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS',86400)
	expires=datetime.now(settings.PYTZ_CONST) + timedelta(seconds=expire_seconds)
	exp=timegm(expires.timetuple())
	dt=datetime.now(settings.PYTZ_CONST)

	salt = uuid.uuid4().hex
	salt=hashlib.sha256( salt.encode() + str(dt).encode()).hexdigest()
    

                  
	payload={
		'iat': int(time.time()),
		'id':id,
		'exp': exp,
		'app_id':application_id,
		'k':kind,
		's':salt
	}
	
	jwt_token={'token': jwt.encode(payload,settings.JWT_AUTH['JWT_SECRET_KEY'])}

	token=jwt_token['token'].decode('utf-8')

	return token
  



def deleteUserToken(user_id,application_id=0):
	'''
	delete tokens of the user

	@input: user_id the id of the user whose token is to be deleted
			application_id the application to which the token belongs too. If it is 0, tokens of the user for any app will be removed
	'''
	fields={'user_id':user_id}
	if application_id>0:
		fields['application_id']=application_id

	tokens=AccessToken.objects.filter(**fields)
	tokens.delete()
	refreshtokens=RefreshToken.objects.filter(**fields)
	refreshtokens.delete()



def clearExpiredTokens():
	'''
	Clear expired tokens
	'''
	from datetime import datetime
	tokens=AccessToken.objects.filter(expires__lt=datetime.now(settings.PYTZ_CONST))
	

	