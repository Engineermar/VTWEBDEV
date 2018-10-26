from django.contrib.auth.models import User

from tools.company import productInformation
from django.utils.translation import ugettext_lazy as _
from tools.generators import generateResetPasswordToken,generateChangeEmailToken
import app.appsettings as appsettings
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.http import JsonResponse
from oauth2_provider.models import AccessToken, Application, RefreshToken
from datetime import datetime,timedelta
from itertools import chain
from tools.tokens import deleteUserToken,createNewApplicationToken,returnMyToken
from app.conf import base as settings
from hr.models import AccountVerification, PasswordReset
from django.contrib.auth import authenticate
from validation.rolechecker import validApplication
from mailer.simplemail import emailResetPasswordLink,emailActivationLink
from validation.pwd import confirmPassword
from django.contrib.auth.models import Permission



class HrData(APIView):
    '''
    Send JSON data simply
    '''
    permission_classes = []

    def get(self,request,format=None):
        data='static/public/hr.json'

        return JsonResponse(data,safe=False,status=200)


class CompanyInformation(APIView):
    '''
    Get company and product details
    '''
    permission_classes = [TokenHasReadWriteScope]

    def get(self,request,format=None):

        product_information=productInformation()

        reply={'company_name':product_information['company_name'],'product_name':product_information['product_name']}

        return JsonResponse(reply,status=200)




class ULogin(APIView):
    '''
    Login
    
    '''

    permission_classes = []
   
    
    def post(self,request,format=None):
       

        
        

        client_id=request.data.get('client_id','')
        client_secret=request.data.get('client_secret','')
        grant_type=request.data.get('grant_type','')
        username=request.data.get('username','')
        pwd=request.data.get('password','')
  

        reply={}
        status=400

    
        try:

            if client_id and client_secret and grant_type:

                application = Application.objects.get(client_id=client_id,client_secret=client_secret,authorization_grant_type=grant_type)
              
                #application exists ok
                #how do we wanna login? Email or phone?
            

                user = authenticate(username=username, password=pwd)

           

                if user is not None:
                    #see if we have a token already

                    continue_token=True #assume nothing is fishy here.

                    
                    #see if they are blocked or not, currently?
                    if user.user_employee.status==0:
                        deleteUserToken(user.id) #incase.
                        reply['detail']=_('ErrorBlockedUser')
                        continue_token=False

                    else:

                        

                        if user.is_active==0:
                            #this aint running due to django 1.10> is_active changes. It is here incase things are reversed back, including the authenrication in settings.py
                            reply['detail']=_('ErrorInactiveUser')
                            continue_token=False


                        #shoud we go on:

                        if continue_token:
                            current_token=returnMyToken(user.id,application.id)
                            access_token_g=''
                            refresh_token_g=''

                            if current_token['token']==None:
                                #not existing. so create a new token
                                deleteUserToken(user.id,application.id) #any reminaning assurance clean up

                        
                            
                                expire_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS',360000)
                                expires = datetime.now(settings.PYTZ_CONST) + timedelta(seconds=expire_seconds)
                               
                                scopes=""

                                for scope in settings.OAUTH2_PROVIDER.get('SCOPES'):
                                    scopes=' '.join([scopes, scope])


                                access_token = AccessToken.objects.create(
                                user=user,
                                application=application,
                                token=createNewApplicationToken(user.id,application.id),
                                expires=expires,
                                scope=scopes)

                                refresh_token = RefreshToken.objects.create(
                                user=user,
                                token=createNewApplicationToken(user.id,application.id,kind='refresh'),
                                access_token=access_token,
                                application=application)

                                access_token_g=access_token.token
                                refresh_token_g=refresh_token.token

                            else:
                                access_token_g=current_token['token']
                                expires=current_token['expires']

                            status=200

                            reply['data'] = {
                            'access_token': access_token_g,
                            'first_name':user.first_name,
                            'last_name':user.last_name,
                            'token_type': 'Bearer',
                            'expire_on':expires
                            }
                          
                            #return permissions
                            #groups=list(user.groups.values_list('id',flat=True))

                            my_permissions=user.user_permissions.all().values_list('codename',flat=True) | Permission.objects.filter(group__user=user).values_list('codename',flat=True)

                            #my_permissions=Permission.objects.filter(group__in=groups).values_list('codename',flat=True)

                            user_permissions=list(set(chain(my_permissions)))

        
                            reply['groups']=user_permissions
                            reply['eid']=user.user_employee.id #employee id

                        
                else:
                    reply['detail']=_('ErrorBadLoginDetails')

            else:
                reply['detail']=_('ErrorBadLoginDetails')
        
        except:
            reply['detail']=_('NoRight')
        


        return JsonResponse(reply,status=status)



class MyRights(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def post(self,request,format=None):

        my_permissions=request.user.user_permissions.all().values_list('codename',flat=True) | Permission.objects.filter(group__user=request.user).values_list('codename',flat=True)
        user_permissions=list(set(chain(my_permissions)))


        reply={'t':user_permissions,'eid':request.user.user_employee.id}
        return JsonResponse(reply,status=200)




class SignOut(APIView):
    def get(self,request,format=None):
        reply={'detail':(_('LogoutOk'))}
        deleteUserToken(request.user.id)
        return JsonResponse(reply,status=200)


class ForgotPwd(APIView):
    '''
    Changes: Oct 18 @5pm. Requires NO token but instead clientid and client password
    '''

    permission_classes = []
    
    def post(self,request,format=None):

        
        email=request.data.get('email','').strip() #what value did they enter?
        client_id=request.data.get('client_id','').strip()
        client_secret=request.data.get('client_secret','').strip()

       
        reply={}
        status=400

        send_email=False

        if not validApplication(client_id,client_secret):
            reply['detail']=_('NoRight')

        else:

            
            try:
              
                user_info=User.objects.get(email=email)
                #is it blocked?
                if user_info.user_employee.status==0:
                    reply['detail']=_('ErrorBlockedUser')
                else:        
             
                    
                    #information was found. So get the data now to email the userr the information
                    token=generateResetPasswordToken()
                    

                    #save the token the passwords table
                    #delete existing first
                    existing_requests=PasswordReset.objects.filter(profile=user_info)
                    existing_requests.delete()

                    pwd_reset=PasswordReset(profile=user_info,unique_code=token)
                    pwd_reset.save()
                    
                    if pwd_reset:
                        #saved. Email the password link to the user now
                        
                        reply['detail']=_('WelcomePwdResetLinkSent')
                        status=200
                        send_email=True
                        
                    else:
                        reply['detail']=(_('ErrorResettingPwd'))

            
            except BaseException as e:
                send_email=False
                reply['detail']=(_('ErrorNoAccount'))

            if send_email:
                try:
                    emailResetPasswordLink(user_info.email, settings.LANGUAGE_CODE,token)
                except:
                    #email couldnt be sent
                    status=400
                    reply['detail']=_('ErrorForgotPasswordEmail')


            
        
        return JsonResponse(reply,status=status)


class ResetPwd(APIView):
    '''
    Given the reset pwd id, give the user the option to change his password
    Weather in get or post, the id should exist
    Note that the id was sent initially to his email from forgot password
    
    Requires no login
    '''
    permission_classes = []

    def get(self,request,token,email,format=None):
        status=400
        reply={}
        try:
            check_token=PasswordReset.objects.values('createdon','profile_id').get(unique_code=token,profile__email=email)
            #exists but is it valid or not? It cant be
            
            createdon=check_token["createdon"]
            now=datetime.now(settings.PYTZ_CONST)
         

            if createdon>now-timedelta(hours=appsettings.APPSET_PWD_RESET_LIFESPAN):
                status=200
                reply['detail']=True
            else:
                reply['detail']=(_('ErrorPwdResetLinkExpired'))
        except:
            reply['detail']=(_('ErrorBadPwdResetLink'))


        return JsonResponse(reply,status=status)


    def post(self,request,token,email,format=None):
        status=400
        reply={}
        try:
            check_token=PasswordReset.objects.get(unique_code=token,profile__email=email)
            #exists but is it valid or not? It cant be
            
            createdon=check_token.createdon
            now=datetime.now(settings.PYTZ_CONST)
         

            if createdon>now-timedelta(hours=appsettings.APPSET_PWD_RESET_LIFESPAN):
                pwd=request.data.get('pwd','').strip()
                pwd_confirm=request.data.get('pwd_confirm','').strip()

                err_msg=confirmPassword(pwd,pwd_confirm)

                if not err_msg:


                    user=User.objects.get(id=check_token.profile_id)
                    if user.user_employee.status==1:
                        user.set_password(pwd)
                        user.save()
                        check_token.delete()
                        status=200
                        reply['detail']=_('PasswordResetOk')
                    else:
                        reply['detail']=_('ErrorBlockedUser')

                else:
                    reply['detail']=err_msg

                
            else:
                reply['detail']=_('ErrorPwdResetLinkExpired')
        except:
            reply['detail']=(_('ErrorBadPwdResetLink'))


        return JsonResponse(reply,status=status)


class ActivateAccount(APIView):
    '''
    Follow a link from an email after registeration. No login required

    Note here, http status is 200, different from others. That is to make it easy from the front end to see and prepare the form/message
    to compensate, tho, we add status in reply (different form http status) to indicate what happend:

    1 =>activated. so message will be displayed
    2 =>blocked. no form to show
    3=> old activation. display message and the form

    4=>activation link missing. show display message

    '''
    permission_classes = []

    def get(self,request,token,email,format=None):
        reply={'status':1} #it was ok
        status=200
        try:
         

            check_token=AccountVerification.objects.get(unique_code=token,email=email)

            createdon=check_token.createdon
            now=datetime.now(settings.PYTZ_CONST)
            email=check_token.email

            if createdon>now-timedelta(hours=appsettings.APPSET_ACCT_ACTIVATION_LIFESPAN):

                user=User.objects.get(email=email)
                if user.user_employee.status==1:
                
                    user.is_active=1
                    user.save()
                    check_token.delete()
                    reply['status']=1
                    reply['detail']=_('AccountActivated')
                else:
                    reply['detail']=_('ErrorBlockedUser')
                    reply['status']=2

            else:
                #

                reply['detail']=(_('ErrorAccountOldActivationCode'))
                reply['status']=3

        except:
            reply['detail']=(_('ErrorAccountActivationCodeMissing'))
            reply['status']=4

        return JsonResponse(reply,status=status)


class ResendActivationLink(APIView):
    '''
    if activation key is old or something, then allow user to generate a new one.

    '''
    permission_classes = []

    def post(self,request,format=None):
        reply={}
        status=400
        
        client_id=request.data.get('client_id','').strip()
        client_secret=request.data.get('client_secret','').strip()
        email=request.data.get('email','').strip()


        if validApplication(client_id,client_secret):
            send_email=False
            try:
                user=User.objects.get(email=email)

                if user.is_active==1:
                    reply['detail']=_('ErrorAlreadyActivated')
                else:
                    if user.user_employee.status==1:
                    #send him/her an activation token
                    #delete existing tokens:
                        existing_tokens=AccountVerification.objects.filter(email=email)
                        existing_tokens.delete()
                        token=generateChangeEmailToken(user.id)
                        account=AccountVerification(unique_code=token,email=email)
                        account.save()
                        status=200

                        
                        send_email=True
                        reply['detail']=_('ActivationLinkSent')
                    else:
                        reply['detail']=_('ErrorBlockedUser')
            except:
                reply['detail']=(_('ErrorAccountActivationMissingEmail'))

            if send_email:
                try:
                    emailActivationLink(token=token,lang=settings.LANGUAGE_CODE,email=email,name=user.first_name)
                except:
                    status=400
                    reply['detail']=_('ErrorActivationSendingEmail')


        else:
            reply['detail']=_('NoRight')

      

        return JsonResponse(reply,status=status)