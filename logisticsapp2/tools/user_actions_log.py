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
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE,ContentType,DELETION

def addNewUserActionLog(log_data):
    '''
    Add logging of user actions that can be seen in the admin area

    @input: log_data is a dictionary with the following keys:
        action==>change,add or delete
        model=>the model affected by the action. If a user is added, User model is affected
        app=> the application label that was affected.

    @output: None

    NOTE: not working properly. Don't use until debugged propelry.
    '''

    flag=""
    if log_data['action']=='change':
        flag=CHANGE
    elif log_data['action']=='add':
        flag=ADDITION
    elif log_data['action']=='delete':
        flag=DELETION
    try:
        content_type_id=ContentType.objects.get(model=log_data['model'],app_label=log_data['app'])
        LogEntry.objects.log_action(
        user_id=log_data['user_id'],
        content_type_id=content_type_id,
        object_id=log_data['row_id'],
        object_repr=log_data['title'],
        action_flag=log_data['flag'],
        change_message=log_data['message']
        )

    except:
        pass
