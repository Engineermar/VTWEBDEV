#Must be logged in to see this area
from django.conf.urls import  url

from hr import views


urlpatterns = [
    url(r'^publish/$', views.Publish.as_view(), name='publish'),
    url(r'^heads-list/$', views.HeadsList.as_view(), name='heads-list'),
    url(r'^heads-add/$', views.HeadAdd.as_view(), name='heads-add'),
    url(r'^heads-edit/(?P<record_id>[0-9]+)/$', views.HeadEdit.as_view(), name='heads-edit'),
    url(r'^heads-information/(?P<record_id>[0-9]+)/$', views.HeadInformation.as_view(), name='heads-information'),
    url(r'^heads-delete/(?P<record_id>[0-9]+)/$', views.HeadDelete.as_view(), name='heads-delete'),

    url(r'^departments-list/(?P<head_id>[0-9]+)/$', views.DepartmentsList.as_view(), name='departments-list'),
    url(r'^departments-add/(?P<head_id>[0-9]+)/$', views.DepartmentAdd.as_view(), name='departments-add'),
    url(r'^departments-information/(?P<record_id>[0-9]+)/$', views.DeparmentInformation.as_view(), name='departments-information'),
    url(r'^departments-edit/(?P<head_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.DepartmentEdit.as_view(), name='departments-edit'),
    url(r'^departments-delete/(?P<head_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.DepartmentDelete.as_view(), name='departments-delete'),

    url(r'^divisions-list/(?P<department_id>[0-9]+)/$', views.DivisionsList.as_view(), name='divisions-list'),
    url(r'^divisions-add/(?P<department_id>[0-9]+)/$', views.DivisionAdd.as_view(), name='divisions-add'),
    url(r'^divisions-edit/(?P<department_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.DivisionEdit.as_view(), name='divisions-edit'),
    url(r'^divisions-information/(?P<record_id>[0-9]+)/$', views.DivisionInformation.as_view(), name='divisions-information'),
    url(r'^divisions-delete/(?P<department_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.DivisionDelete.as_view(), name='divisions-delete'),

    url(r'^units-list/(?P<division_id>[0-9]+)/$', views.UnitsList.as_view(), name='units-list'),
    url(r'^units-add/(?P<division_id>[0-9]+)/$', views.UnitAdd.as_view(), name='units-add'),
    url(r'^units-edit/(?P<division_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.UnitEdit.as_view(), name='units-edit'),
    url(r'^units-delete/(?P<division_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.UnitDelete.as_view(), name='units-delete'),

    url(r'^professions-list/(?P<paginated>[0-9]+)/$', views.ProfessionsList.as_view(), name='professions-list'),
    url(r'^professions-add/$', views.ProfessionAdd.as_view(), name='professions-add'),
    url(r'^professions-edit/(?P<record_id>[0-9]+)/$', views.ProfessionEdit.as_view(), name='professions-edit'),
    url(r'^professions-delete/(?P<record_id>[0-9]+)/$', views.ProfessionDelete.as_view(), name='professions-delete'),

    url(r'^offices-list/(?P<hr_kind>[hdvu]{1})/(?P<hr_id>[0-9]+)/$', views.OfficesList.as_view(), name='offices-list'),
    url(r'^office-add/$', views.OfficeAdd.as_view(), name='office-add'),
    url(r'^office-edit/(?P<id>[0-9]+)/$', views.OfficeEdit.as_view(), name='office-edit'),
    url(r'^office-delete/(?P<id>[0-9]+)/$', views.OfficeDelete.as_view(), name='office-delete'),

   

]