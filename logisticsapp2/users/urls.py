#Must be logged in to see this area
from django.conf.urls import  url

from users import views


urlpatterns = [
	url(r'^new/$', views.RegisterNew.as_view(), name='register'),
    url(r'^users-list/$', views.ListProgramUsers.as_view(), name='users-list'),
    url(r'^delete/$', views.DeleteUser.as_view(), name='delete'),
    url(r'^delete-position/$', views.DeletePosition.as_view(), name='delete-position'),
    url(r'^position-state/$', views.ActivateDeactivatePosition.as_view(), name='position-state'),
    url(r'^strip-role/$', views.StripRoles.as_view(), name='strip-role'),
    url(r'^toogle-active-status/$', views.ActivateDeactivateUser.as_view(), name='toogle-active-status'),
    url(r'^reset-password/$', views.UserResetPassword.as_view(), name='reset-password'),
    url(r'^roles/(?P<user_id>[0-9]+)/$', views.UserRoles.as_view(), name='roles'),
    url(r'^positions/(?P<emp_id>[0-9]+)/$', views.EmployeePositions.as_view(), name='positions'),
    url(r'^update-role/$', views.UpdateRoles.as_view(), name='update-role'),
    url(r'^rights/$', views.ListUserRights.as_view(), name='rights'),
    url(r'^position-info/(?P<position_id>[0-9]+)/$', views.EmployeeFromPosition.as_view(), name='position-info'),
    url(r'^workingin/(?P<kind>[a-z]{1})/(?P<kind_id>[0-9]+)/$', views.EmployeesWorkingIn.as_view(), name='workingin'),
    url(r'^my-positions/$', views.MyHRInformation.as_view(), name='my-positions'),

]