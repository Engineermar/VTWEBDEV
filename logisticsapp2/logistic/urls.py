#Must be logged in to see this area
from django.conf.urls import  url

from logistic import views


urlpatterns = [
    
    url(r'^incoming-new/(?P<invoice_id>[0-9]+)/$', views.NewIncoming.as_view(), name='incoming-new'),
    url(r'^tags/(?P<invoice_id>[0-9]+)/$', views.Tags.as_view(), name='tags'),
    url(r'^edit-incoming/(?P<invoice_id>[0-9]+)/$', views.EditIncomingInvoice.as_view(), name='edit-incoming'),

    url(r'^provider-add/$', views.ProviderAdd.as_view(), name='provider-add'),
    url(r'^provider-search/$', views.ProviderSearch.as_view(), name='provider-search'),
    url(r'^provider-edit/(?P<id>[0-9]+)/$', views.ProviderEdit.as_view(), name='provider-edit'),
    url(r'^provider-delete/(?P<id>[0-9]+)/$', views.ProviderDelete.as_view(), name='provider-delete'),

    url(r'^provider-kind-add/$', views.ProviderKindAdd.as_view(), name='provider-kind-add'),
    url(r'^provider-kind-edit/(?P<kind_id>[0-9]+)/$', views.ProviderKindEdit.as_view(), name='provider-kind-edit'),
    url(r'^provider-kind-delete/(?P<kind_id>[0-9]+)/$', views.ProviderKindDelete.as_view(), name='provider-kind-delete'),
    url(r'^provider-kind-list/$', views.ProviderKinds.as_view(), name='provider-kind-list'),

    url(r'^delete-incoming-item/(?P<invoice_id>[0-9]+)/(?P<item_id>[0-9]+)/$', views.DeleteItem.as_view(), name='delete-incoming-item'),
    url(r'^edit-incoming-item/(?P<invoice_id>[0-9]+)/(?P<item_id>[0-9]+)/$', views.EditItem.as_view(), name='edit-incoming-item'),

    url(r'^invoice-incoming/(?P<invoice_id>[0-9]+)/(?P<option>[a-zA-Z]+)/$', views.PrintableIncomingInvoice.as_view(), name='invoice-incoming'),
    url(r'^invoice-incoming-search/$', views.IncomingInvoicesList.as_view(), name='invoice-incoming-search'),

    url(r'^outgoing-new/$', views.NewOutgoing.as_view(), name='outgoing-new'),
    url(r'^invoice-outgoing/(?P<invoice_id>[0-9]+)/(?P<option>[a-zA-Z]+)/$', views.PrintableOutgoingInvoice.as_view(), name='invoice-outgoing'),
    url(r'^invoice-outgoing-search/$', views.OutgoingInvoicesList.as_view(), name='invoice-outgoing-search'),

    url(r'^request-new/$', views.NewRequest.as_view(), name='request-new'),
    url(r'^process-request/$', views.ProcessRequest.as_view(), name='process-request'),
    url(r'^stockedout-items-list/(?P<invoice_id>[0-9]+)/$', views.StockedOutItemsList.as_view(), name='stockedout-items-list'),
    url(r'^stockout-item-update-status/$', views.UpdateStatusStockedOutItem.as_view(), name='stockout-item-update-status'),
    url(r'^request-revoke/$', views.RevokeRequest.as_view(), name='request-revoke'),
    url(r'^my-requests/$', views.MyRequests.as_view(), name='my-requests'),
    url(r'^view-requests/$', views.ClientRequests.as_view(), name='view-requests'),
    url(r'^request-detail/(?P<invoice_id>[0-9]+)/$', views.ClientRequestDetail.as_view(), name='request-detail'),
    url(r'^invoice-request/(?P<invoice_id>[0-9]+)/(?P<source>[a-zA-Z]+)/$', views.PrintableRequestInvoice.as_view(), name='invoice-request'),
    url(r'^outgoing-reverse/$', views.ReverseOutgoing.as_view(), name='outgoing-reverse'),
    url(r'^outgoing-edit-qty/$', views.UpdateStockedOutItemQuantity.as_view(), name='outgoing-edit-qty'),
    url(r'^browse-items/(?P<give>[a-zA-Z]{2,3})/$', views.SearchItems.as_view(), name='browse-items'),

    url(r'^items-in-possession/(?P<option>[a-zA-Z]+)/(?P<show>[1-3]{1})/(?P<return_entity_info>[a-z]{1})/$', views.ItemsInPossession.as_view(), name='items-in-possession'),


    url(r'^return-new/$', views.ReturnSpecifiedItems.as_view(), name='return-new'),
    url(r'^return-reverse/$', views.ReverseReturn.as_view(), name='return-reverse'),
    url(r'^invoice-return/(?P<invoice_id>[0-9]+)/(?P<option>[a-zA-Z]+)/$', views.PrintableReturnInvoice.as_view(), name='invoice-return'),
    url(r'^invoice-return-search/$', views.ReturnInvoicesList.as_view(), name='invoice-return-search'),
    url(r'^returned-items-list/(?P<invoice_id>[0-9]+)/$', views.ReturnedItemsList.as_view(), name='returned-items-list'),
    url(r'^returned-item-update-status/$', views.UpdateStatusReturnedItem.as_view(), name='returned-item-update-status'),

    url(r'^transfer-new/$', views.NewTransfer.as_view(), name='transfer-new'),
    url(r'^transfer-reverse/$', views.ReverseTransfer.as_view(), name='transfer-reverse'),
    url(r'^transfered-items-list/(?P<invoice_id>[0-9]+)/$', views.TransferedItemsList.as_view(), name='transfered-items-list'),
    url(r'^invoice-transfer/(?P<invoice_id>[0-9]+)/(?P<option>[a-zA-Z]+)/$', views.PrintableTransferInvoice.as_view(), name='invoice-transfer'),
    url(r'^transfer-item-update-status/$', views.UpdateStatusTransferItem.as_view(), name='transfer-item-update-status'),

    url(r'^update-status/(?P<tag>[a-zA-Z0-9-]+)/(?P<new_status>[a-zA-Z]+)/$', views.ChangeItemStatus.as_view(), name='update-status'),

    url(r'^report-as-lost/(?P<tag>[a-zA-Z0-9-]+)/$', views.ReportItemAsLost.as_view(), name='report-as-lost'),
    url(r'^report-as-found/(?P<tag>[a-zA-Z0-9-]+)/(?P<store_id>[0-9]+)/(?P<new_status>[a-zA-Z]+)/$', views.ReportLostItemAsFound.as_view(), name='report-as-found'),


    url(r'^items-instore/$', views.ItemsInStore.as_view(), name='items-instore'),
    url(r'^move-items-tostore/$', views.MoveItemsInStore.as_view(), name='move-items-tostore'),
    url(r'^store-tostore/$', views.StoreToStore.as_view(), name='store-tostore'),
    url(r'divide-place/$', views.DividePlace.as_view(), name='divide-place'),
    url(r'batch-update/$', views.BatchUpdateItemStatus.as_view(), name='batch-update'),
    url(r'inventory/$', views.Inventory.as_view(), name='inventory'),
    url(r'soft-transfer/$', views.SoftTransfer.as_view(), name='soft-transfer'),

  

]