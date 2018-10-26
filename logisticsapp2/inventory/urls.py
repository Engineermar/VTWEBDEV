#Must be logged in to see this area
from django.conf.urls import  url

from inventory import views



urlpatterns = [
    url(r'^categories-list/$', views.CategoriesList.as_view(), name='categories-list'),
    url(r'^categories-add/$', views.CategoryAdd.as_view(), name='categories-add'),
    url(r'^categories-merge/$', views.MergeCategory.as_view(), name='categories-merge'),
    url(r'^categories-edit/(?P<record_id>[0-9]+)/$', views.CategoryEdit.as_view(), name='categories-edit'),
    url(r'^categories-delete/(?P<record_id>[0-9]+)/$', views.CategoryDelete.as_view(), name='categories-delete'),
    
    url(r'^category-info/(?P<record_id>[0-9]+)/$', views.CategoryInformation.as_view(), name='categories-edit'),



    url(r'^products-list/(?P<category_id>[0-9]+)/$', views.ProductsList.as_view(), name='products-list'),
    url(r'^products-add/(?P<category_id>[0-9]+)/$', views.ProductAdd.as_view(), name='products-add'),
    url(r'^products-mv-cat/$', views.MoveProductsToCategory.as_view(), name='products-mv-cat'),
    url(r'^products-merge/$', views.MergeProducts.as_view(), name='products-merge'),



    url(r'^products-edit/(?P<category_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.ProductEdit.as_view(), name='products-edit'),
    url(r'^products-delete/(?P<category_id>[0-9]+)/(?P<record_id>[0-9]+)/$', views.ProductDelete.as_view(), name='products-delete'),
    
    url(r'^brands-list/$', views.BrandsList.as_view(), name='brands-list'),
    url(r'^brands-add/$', views.BrandAdd.as_view(), name='brands-add'),
    url(r'^brands-edit/(?P<record_id>[0-9]+)/$', views.BrandEdit.as_view(), name='brands-edit'),
    url(r'^brands-delete/(?P<record_id>[0-9]+)/$', views.BrandDelete.as_view(), name='brands-delete'),

    url(r'^manf-list/$', views.ManufacturersList.as_view(), name='manf-list'),
    url(r'^manf-add/$', views.ManufacturerAdd.as_view(), name='manf-add'),
    url(r'^manf-edit/(?P<record_id>[0-9]+)/$', views.ManufacturerEdit.as_view(), name='manf-edit'),
    url(r'^manf-delete/(?P<record_id>[0-9]+)/$', views.ManufacturerDelete.as_view(), name='manf-delete'),

    url(r'^stores-list/$', views.StoresList.as_view(), name='stores-list'),
    url(r'^stores-add/$', views.StoreAdd.as_view(), name='stores-add'),
    url(r'^stores-edit/(?P<record_id>[0-9]+)/$', views.StoreEdit.as_view(), name='stores-edit'),
    url(r'^stores-delete/(?P<record_id>[0-9]+)/$', views.StoreDelete.as_view(), name='stores-delete'),
   


]