import datetime
import re
# DATEFORMATS - once done move to a settings or to db
EP_DATE_FORMAT_SUBCODE = '%Y/%m/%d'
EP_DATE_FORMAT_1 = '%Y%m%d'
EP_DATE_FORMAT_2 = '%m/%d/%Y'
GS_DATE_FORMAT = "%m-%d-%Y"

CUSTOMER_CODE_EXPR = r'[^0-9a-zA-Z]+'

def create_customer_code(customer_description):
	# need to replace all nonalpha chars with a space
	expr = CUSTOMER_CODE_EXPR
	customer_code_length = 19
	s = re.sub(expr, ' ', customer_description)
	return ''.join([x[:4].upper() for x in s.split(' ')])[:customer_code_length]



def create_customer_code2(customer_description, duplicates=0):
	split_name = customer_description.upper().split()

	if len(split_name) == 1:
		return customer_description

	first4 = split_name.pop(0)[:4]

	return first4 + ''.join([x[:2] for x in split_name])


def format_goshow_date(date, datetype):
	
	if not date:
		return ''

	if datetype == 0:
		_dt = datetime.datetime.strptime(date, GS_DATE_FORMAT)
		return _dt.strftime(EP_DATE_FORMAT_SUBCODE)
	
	if datetype == 1:
		_dt = datetime.datetime.strptime(date, GS_DATE_FORMAT)
		return _dt.strftime(EP_DATE_FORMAT_1)
	
	if datetype == 2:
		_dt = datetime.datetime.strptime(date, GS_DATE_FORMAT)
		return _dt.strftime(EP_DATE_FORMAT_2)

class CardTypeInvalidException(Exception): pass
def get_ep_payment_type(payment):
	# payment_types = dict(
	# 	CASH       = 0,
	# 	CHECK      = 1,
	# 	MASTERCARD = 2,
	# 	VISA       = 2,
	# 	DISCOVER   = 2,
	# 	dinners    = 3,
	# 	amex       = 3
	# )

	payment_type = payment.get('payment_type').lower()
	
	if payment_type in ['credit', 'credit card']:
		# what if no card type?
		try:
			card_type = payment.get('credit_card_type').lower()
		except CardTypeInvalidException, e:
			raise e
			
		if card_type:
			if card_type in ['dinners', 'amex']:
				return 3
			else:
				return 2
	if payment_type == 'check':
		return 1

	if payment_type == 'cash':
		return 0
	return 0

def get_ep_item_number(gs_item):
	return gs_item.get('Item name')

def get_ep_card_id(credit_card_type):
	_cc_type = credit_card_type.lower()
	
	card_types = {
		'master': 'MASTER', 
		'visa': 'VISA', 
		'american': 'AMEX', 
		'amex': 'AMEX', 
		'diners': 'DINERS', 
		'disco':'DISCOVER'
	}

	for key, value in card_types.items():
		if key in _cc_type:
			return value

def get_ep_country_code(gs_country_code):
	if 'united states' in gs_country_code.lower():
		return 'USA'
	return ''
