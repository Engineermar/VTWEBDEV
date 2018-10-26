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
from django.utils.translation import ugettext_lazy as _
from app.conf import base as settings
import os
import app.appsettings as appsettings
from dateutil import parser
from datetime import date,timedelta #for checking renewal date range.


def isDateValid(value,criteria,max_age=0,min_age=0):
    '''
    Is the given date valid or not?
    @input: value the date to be checked
            criteria how the check is to happen. It can be
                past
                pastornow
                future
                futureornow
    
            max_age maximum "age" it can be, in relation to today. ignore if 0
            min_age min "age" it can be in relation to today. ignore if 0

    if max_age and min_age are given, the date must lie ine between those based on today E.g. value=1990-03-03, max_age=40
    since max_age=100 and today is 2018-03-03, it will be invalid since hte difference is above 40 years old
    
    @output: boolean true or false
    '''
    
    reply=False
    
    if value:
        
        #convert value to date.
        try:
            today=date.today()
            value=parser.parse(str(value)).date()
            option=criteria.lower()

            if option=='past':
                #date must be in the past
                if value<today:
                    reply=True
            elif option=='pastornow':
                if value<=today:
                    reply=True
            elif option=='future':
                if value>today:
                    reply=True
            elif option=='futureornow':
                if value>=today:
                    reply=True
            elif option=='any':
                #care about its valid format only
                reply=True

            if reply:
                if max_age>0:
                    if today.year-value.year>max_age:
                        reply=False
                if min_age>0:
                    if value.year + min_age > today.year:
                        reply=False


        except BaseException as e:
            reply=False 

    return reply


def validateCharacters(value,field_name,replace_them=False):
    '''
    We have a predefined list of character names that are not valid in app/mysettings.py/APPSET_INVALID_CHARACTERS
    On top, we must always make sure there is no | in the value to be validated.
    if replace with is True, then dont replace. Instead return back the error. Error replace the badcharacters and move on

    @input: value the value to be checked
            field_name name of the field in a friendly term (.e.g First Name)
            replace_them: if found invalid characters, do I replace htem or not? True for yes else false.

    @output: error message if replace_them is False. If true, a new string with invalid characters replaced.

    replacement string is defined in app/appsettings.APPSET_INVALID_CHARACTERS_REPLACE_WITH
    '''
    invalid_chars=appsettings.APPSET_INVALID_CHARACTERS

    if "|" not in invalid_chars:
        invalid_chars=''.join([invalid_chars,"|"])

    if replace_them:
        invalid_chars='[' + invalid_chars + ']'
        new_value = re.sub(invalid_chars, appsettings.APPSET_INVALID_CHARACTERS_REPLACE_WITH, value)
        return new_value



    #check if value contains any of the invalid characters now
    invalid_chars_l=[]
    for c in invalid_chars:
        invalid_chars_l.append(c)

    
    errmsg=''

    if any(x in value for x in invalid_chars_l):
        errmsg=_('ErrorGenericInvalidCharacters') % {'field_name':field_name,'chars':invalid_chars}

    return errmsg


def validateLogo(value):
    '''
    Make sure uploaded logo image is valid. Not in use anymore. Here for just in case purpose

    value is request object
    '''

    #value is request.data here

    ext = os.path.splitext(value['logo'].name)[1]  # [0] returns path+filename
    max_allowed_file_size=int(settings.LOGO_MAX_FILE_SIZE)
    errmsg={}

   
    valid_extensions = ['.png','.jpg']
    if not ext.lower() in valid_extensions:
    	errmsg['image_type']=_('ErrorInvalidImageType')

    if value['logo'].size>max_allowed_file_size:
    	errmsg['image_size']=_('ErrorLargeLogoSize') % {'size':str(max_allowed_file_size)}

    return errmsg