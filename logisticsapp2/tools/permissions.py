from django.contrib.auth.models import User
from django.db.models import Q

def usersWithPermission(perm):
	'''
	Return a list of users with the specific permission

	@input: perm: an array list of permissions

	@output: list of users who are are active, unblocked and have the permission assigned to them individually or are part of a group with the specified permission
	'''
	#perm = Permission.objects.filter(codename__in=perm).values_list('id',flat=True) 
	users = User.objects.filter(Q(is_active=1),Q(user_employee__status=1),Q(groups__permissions__codename__in=perm) | Q(user_permissions__codename__in=perm)).values('id','first_name','last_name','email').distinct()

	return list(users)

