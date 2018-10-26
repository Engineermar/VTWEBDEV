'''
 * Logistics Management System
 *
 * Developed by RLRC, Kigali, Rwanda 2016-2017. All Rights Reserved
 *
 * This content is protected by national and international patent laws.
 *
 * Possession and access to this content is granted exclusively to Developers
 * of RLRC while full ownership is granted only to RLRC company.
 
 *
 * @package	LMS-RLCR
 * @author	Kiflemariam Sium (kmsium@gmail.com || sium@go.rw || sium@iconicdatasystems.com)
 * @copyright	Copyright (c) RLRC, 2017
 * @license	http://www.rlrc.gov.rw
 * @link	http://www.rlrc.gov.rw
 * @since	Version 1.0.0
 * @filesource
 '''
from django.db import models




'''
All models are dummy and purely (i.e. managed=False) for permission purposes since Django permissions are model-attached

Courtesy of  https://stackoverflow.com/a/37988537/4569596

Note; default_permissions=() must be set before migrations happen
'''




class PermissionViewReport(models.Model):
	'''
	Rights related to viewing reports
	'''

	class Meta:
		managed=False
		default_permissions = ()

		permissions=(
			('rpt_instore', 'Report Instore Items'),
			('rpt_expiring_items', 'Report Expiring Items'),
			('rpt_finishing_items', 'Report Finishing Items'),
			('rpt_item_history', 'Report Item History'),
			('rpt_entity_history', 'Report Entity History'),
			('rpt_suppliers', 'Report Suppliers'),
			('rpt_distribution', 'Report Distribution'),
			('rpt_inventory', 'Report Inventory'),
			('rpt_product_flow', 'Report Product Flow'),
			('rpt_stockins', 'Report Stock Ins'),
			('rpt_depreciation', 'Report Depreciation'),
			('rpt_monthlyreport','Monthly InStore Report'),
			('rpt_finreport','Financial Report')
			)

class PermissionVisualizations(models.Model):
	'''
	Rights related to viewing visualizations/charts
	'''

	class Meta:
		managed=False
		default_permissions = ()

		permissions=(
			('visualization_purchases', 'Purchased Items Visualizations'),
			('visualization_purchases_timeseries', 'Purchased Items Time Series Visualizations'),
		
			)

class PermissionExtra(models.Model):
	'''
	extra permissions
	'''

	class Meta:
		managed=False
		default_permissions = ()

		permissions=(
			('extra_view_manage_hr', 'View for Manage HR'),
			('extra_view_manage_catalog', 'View for Manage Catalog'),
			('extra_view_suppliers', 'View Suppliers'),
			('extra_print_purchase_invoice', 'View or Print Purchase Invoice'),
			('extra_print_distribution_invoice', 'View or Print Distribution Invoice'),
			('extra_view_purchases_invoices', 'View List of Purchase Invoices'),
			('extra_view_distribution_invoices', 'View List of Distribution Invoices'),
			('extra_view_inpossession_items', 'View List of Items With An Entity'),
			('extra_print_return_invoice', 'View or Print Return Invoice'),
			('extra_view_return_invoices', 'View List of Return Invoices'),
			('can_make_transfers', 'Can Make Transfers'),
			('extra_print_transfer_invoice', 'View or Print Transfer Invoice'),
			('can_change_item_status', 'Can Change Item Status'),
			('can_report_lost_items', 'Can Report Lost Items'),
			('can_report_found_items', 'Can Report Found Items'),
			('can_view_tech_services', 'Can View Tech Services'),
			('can_view_users', 'Can View Users'),
			('can_view_positions', 'Can View Employee Positions'),
			('can_strip_user_roles', 'Can Strip User Roles'),
			('can_act_deact_user', 'Can Activate Deactivate Users'),
			('extra_reset_userpassword', 'Can Reset User Password'),
			('can_view_user_rights', 'Can View User Rights'),
			('can_update_user_rights', 'Can Update User Rights'),
			('can_remove_user_right', 'Can Remove User Right'),
			('can_add_user_role', 'Can Add User Right'),
			('extra_view_cat_products','View Products of Category'),
			('extra_view_head_department','View Departmetns of Head'),
			('extra_view_department_divisions','View Divisions of Department'),
			('extra_view_division_units','View Units of Division'),
			('extra_can_delete_emp_from_hr','Can Delete Employee From Position'),
			('extra_can_move_emp_in_hr','Can Move Employee In HR'),
			('extra_can_print_requests_form','Can Print Requets Form'),
			('reverse_transfer','Reverse Transfer'),
			('email_get_request_notification','Accept Email Notification On New Request'),
			('can_print_tags','Can Print Item Tags'),
			('can_move_instore_items','Can Move Instore Items'),
			('can_move_from_store_to_store','Can Move Store to Store in Full'),
			('manage_instore_items','Manage In Store Items'),
			('can_divide_place','Can Divide and Place Consumables'),
			('manage_inventory_items','Manage Inventory Items'),
			('can_make_soft_transfer','Can Make Soft Transfer'),
			('can_accept_expiry_items_notification','Receive Expiring Items Email Notification'),
			('can_accept_low_stock_notification','Receive Low Stock Items Email Notification'),
			('can_merge_categories','Can Merge Categories'),
			('can_move_products_to_categories','Can Move Products to Categories'),
			('can_merge_products','Can Merge Products'),
			('can_view_returend_items_list','Can View Returned Items List'),
			('can_edit_returend_items_status','Can Edit Returned Items Status'),
			('can_view_tranfered_items_list','Can View Transfered Items List'),
			('can_edit_transfered_items_status','Can Edit Transfered Items Status'),
			('reverse_outgoing','Reverse Stock Out'),
			('can_view_stocked_out_items_list','Can View Stocked Out Items List'),
			('can_edit_stocked_out_items_status','Can Edit Stocked Out Items Status'),
			('can_edit_stocked_quantity','Can Edit Stocked Out Items Quantity'),
			('can_actdec_emp_positions','Can Activate-Deactivate Employee Postions'),
			


			)
