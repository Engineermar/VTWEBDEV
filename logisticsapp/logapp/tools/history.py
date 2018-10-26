from logistic.models import ItemUnconventionalHistory

from datetime import date

def addItemHistory(item_id,history,user_id):
	'''
	Add history to a particular item that is not "conventional" in nature. By unconventional, it means a particular action has broken
	the life-cycle of a specific product.

	A normal life-cycle of an item is:

	purchased=>stored=>distributed=>returned=>distributed=>depreciated

	but an item could be stolen from the store or lost by an employee? That action is labelled as unconvenational but still forms history of the product

	@input item_id:datbase id of the item in question
	@input history: the action that happened
	@user_id: the user who is registering the history
	'''
	
	addHistory=ItemUnconventionalHistory(item_id=item_id,reportedon=date.today(),factor=history,processedby_id=user_id)
	addHistory.save();
