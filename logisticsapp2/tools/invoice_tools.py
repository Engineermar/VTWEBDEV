from datetime import date,timedelta #for checking renewal date range.
import app.appsettings as appsettings


def invoiceIsEditable(processedon):
	'''
	Based on the date it was processed, an invoice should be locked from being editing. Invoice here refers to incoming/stocking, trnasfers
	returns and distribution

	@processedon: the date the processing happened

	return true if it can be altered or false.

	Depends on APPSET_EDITINVOICE_AGE which is number of days after which the invoice can be altered
	'''
	reply=False #by default it can be altered

	days_valid=appsettings.APPSET_EDITINVOICE_AGE

	#for any invoice to be editable, it must be only days_valid old
	today=date.today()

	allowed_date= today + timedelta(days=int(days_valid))
	if processedon<allowed_date:
		reply=True

	return reply



