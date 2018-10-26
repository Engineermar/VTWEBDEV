from rest_framework import serializers
from validation.pwd import confirmPassword
from django.utils.translation import ugettext_lazy as _


class ChangePwdSerializer(serializers.Serializer):
	'''
	Change Password Serializer here
	'''
	password_current=serializers.CharField(max_length=16,allow_blank=False,required=True)
	password=serializers.CharField(max_length=16,allow_blank=False,required=True)
	password_new=serializers.CharField(max_length=16,allow_blank=False,required=True)
	
	
	def __init__(self,*args,**kwargs):
		self.user=kwargs.pop('user')
		super(ChangePwdSerializer, self).__init__(*args, **kwargs)
	

	def validate(self,data):
		pwd=data['password']
		pwd_current=data['password_current']
		pwd_new=data['password_new']
		errmsg={}

		if not pwd_current:
			errmsg['password_current']=(_('ErrorSecurityCurrentPwdEmpty'))
		
		else:
			if not self.user.check_password(pwd_current):
				errmsg['password_current']=(_('ErrorSecurityCurrentPwdBad'))
		

		if not pwd:
			errmsg['password']=(_('ErrorSecurityNewPwdEmpty'))
		else:
			check=confirmPassword(pwd,pwd_new)

			if check:
				errmsg['password']=(_(check))

		
		if errmsg:
			raise serializers.ValidationError(errmsg)
		
		return data