
from django.contrib import admin
from appowner.models import Information,Configuration,DefaultUserGroup

# Register your models here.

class InformationAdmin(admin.ModelAdmin):
	list_dispaly=('name','tele','email','idcode')
	exclude=('code',)

	def save_model(self, request, obj, form, change):
		#there can be only one update.
		if change: #only change can happen. Recall there is a default information stored
			
			obj.save()
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False
	
	def get_actions(self,request):
		#disable delete select box
		actions = super(InformationAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions


	def delete_model(self, request, obj):
		#Shouldn't be deleted.
		return False

class ConfigurationAdmin(admin.ModelAdmin):
	list_dispaly=('enable_emailing','auto_activate_users')
	exclude=('code',)

	def save_model(self, request, obj, form, change):
		#there can be only one update.
		if change: #only change can happen. Recall there is a default information stored
			obj.save()
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False
	
	def get_actions(self,request):
		#disable delete select box
		actions = super(ConfigurationAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions


	def delete_model(self, request, obj):
		#Shouldn't be deleted.
		return False


class DefaultUserGroupAdmin(admin.ModelAdmin):
	list_dispaly=('group')
	
	def has_add_permission(self, request):
		return False if self.model.objects.count() > 0 else super().has_add_permission(request)
	

admin.site.register(Information,InformationAdmin)
admin.site.register(Configuration,ConfigurationAdmin)
admin.site.register(DefaultUserGroup,DefaultUserGroupAdmin)
