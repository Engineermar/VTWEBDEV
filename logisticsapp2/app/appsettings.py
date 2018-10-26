'''
* These are custom settings used by the application. They differ from settings.py in that they don't include system related settings.
For every modification you do, you must modify .po language files and compile them to reflect the changes
All settings must start with APPSET_

RPT_V settings refer to time series reports
'''
from django.utils.translation import ugettext_lazy as _


APPSET_YES_NO=(('Yes',_('Yes')), ('No',_('No')))
APPSET_INVALID_CHARACTERS='|~'
APPSET_INVALID_CHARACTERS_REPLACE_WITH='*'
APPSET_NUMBER_OF_JOBS_TOSHOW=20
APPSET_NUMBER_OF_USERS_TO_SHOW=40
APPSET_NUMBER_OF_INSTORE_ITEMS=40
INVOICES_PER_PAGE=35
APPSET_EDITINVOICE_AGE=30
APPSET_DEFAULT_EXPIRYDAYS=30
APPSET_EXPIRAYDATE_BACKWORDDAYS=5
APPSET_EXPIRAYDATE_FORWARDDAYS=15
APPSET_PWD_RESET_LIFESPAN=48
APPSET_ACCT_ACTIVATION_LIFESPAN=48
APPSET_ALERT_EXPIRY_DAYS=14
APPSET_RPT_V_TS_PURCHASE_STARTYEAR=2012
APPSET_RPT_V_TS_MAX_PERIOD=24 #24 Years or 24 Months