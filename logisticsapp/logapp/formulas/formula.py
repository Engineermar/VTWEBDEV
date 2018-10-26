from datetime import date,timedelta #for checking renewal date range.

def salvageValueCalculator(price,dep_rate,life_span):
	'''
	return savlage value of an asset. For more please, visit the URL:
		https://www.accountingcapital.com/assets/how-to-calculate-depreciation-rate/

	@input: price => pricie of the item
			dep_rate==>depreatication rate of the product
			life_span=>the number of years the product is supposed to live

	@output: salvage value in floating/decimal format
	'''

	price=float(price)
	life_span=int(life_span)
	dep_rate=float(dep_rate)

	deps=(1-dep_rate)**life_span

	return round(price * deps,2)


	
def depreciationCalculator(lifespan,depreciation_method,arrivedon,salvagevalue,purchase_price):
	'''
	depreciation calculator.

	Candidate for deletion; please don't use.
	'''

	today=date.today()
	reply=['','','']
	arrivedin_year=arrivedon.year
	die_on_date=date(arrivedon.year + lifespan,arrivedon.month,arrivedon.day) #arrivedon + timedelta(year=lifespan)
	
	dep_value=0
	if depreciation_method=='StraightLine':
		depreciable_cost=purchase_price - salvagevalue
		annual_dep_cost=depreciable_cost / lifespan
		dep_value=purchase_price - (lifespan)  * annual_dep_cost
	elif depreciation_method=='DoubleDecline':
		dep_rate= (100/lifespan) * 2;
		dep_value= (purchase_price * dep_rate)/100 ;

	reply[0]=die_on_date
	reply[1]=dep_value
	reply[2]=die_on_date.year

	return reply
