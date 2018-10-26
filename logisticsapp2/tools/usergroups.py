from django.contrib.auth.models import Group
from appowner.models import DefaultUserGroup
class DefaultUserGroups():
	'''
	Each user belongs to certain groups for a specific client. The groups define permissions.

	Regardless of actual group names, here we define list of possible roles that map to the group names in django.auth

	Return: group object

	Note: will be changed in next release to avoid hard-coded user Group names.


	'''

	def __requestedGroup(self,group_name):
		'''
		Private method that actually returns the requested group
		'''
		try:
			return Group.objects.get(name=group_name)

		except:
			return None


	def default(self):
		'''
		Default group as stored in DefaultUserGroup model (set in admin area)
		'''

		
		groups=list(DefaultUserGroup.objects.all().values('group__name'))
		if groups:
			group_name=groups[0]['group__name']
			return self.__requestedGroup(group_name=group_name)

		return None
	

		#return self.__requestedGroup(group_name='Employee')


	def giver(self):
		'''
		Giver group. Note that giver shouldnt necessarily be the same as in the auth.groups.name. it is determined by group_name='Giver'
		'''
		return self.__requestedGroup(group_name='Giver')

	def admin(self):
		return self.__requestedGroup(group_name='Manager')

	def finance(self):
		return self.__requestedGroup(group_name='DAF')


	def stocker(self):
		return self.__requestedGroup(group_name='Stocker')

	def reporter(self):
		return self.__requestedGroup(group_name='Reporter')



