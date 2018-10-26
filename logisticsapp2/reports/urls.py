#Must be logged in to see this area
from django.conf.urls import  url

from reports import views


urlpatterns = [
    url(r'^instore/$', views.InStore.as_view(), name='instore'),
    url(r'^expiring/$', views.ExpiringItems.as_view(), name='expiring'),
    url(r'^finishing/$', views.FinishingProducts.as_view(), name='finishing'),
    url(r'^item-history/$', views.ItemHistory.as_view(), name='item-history'),
    url(r'^entity-history/(?P<e_kind>[a-zA-Z]+)/(?P<e_id>[0-9]+)/$', views.EntityHistory.as_view(), name='entity-history'),
    url(r'^suppliers/$', views.Suppliers.as_view(), name='suppliers'),
    url(r'^distribution/$', views.Distribution.as_view(), name='distribution'),
    url(r'^inventory/$', views.Inventory.as_view(), name='inventory'),
    url(r'^product-flow/(?P<product_id>[0-9]+)/$', views.ProductFlow.as_view(), name='product-flow'),
    url(r'^stockin/$', views.StockedIn.as_view(), name='stockin'),
    url(r'^depreciation/$', views.Depreciation.as_view(), name='depreciation'),
    url(r'^items-withme/$', views.ItemsInMyHand.as_view(), name='items-withme'),
    url(r'^monthly-report/(?P<month>[0-9]+)/(?P<yr>[0-9]+)/$', views.MonthlyReport.as_view(), name='monthly-report'),
    url(r'^fin/$', views.Financial.as_view(), name='fin'),

    url(r'^v-purchases/$', views.VisualizationPurchase.as_view(), name='v-purchases'),
    url(r'^v-purchases-ts/$', views.VisualizationPurchaseTimeline.as_view(), name='v-purchases-ts'),
]