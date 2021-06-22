"""
Functions for sorting and parsing GoShow's EventPath report
"""
from .epformats import format_goshow_date
# module to organize the data from goshow by customer


# order items are showing up more than once
# adama = [x for x in orders if x['customer'] == 'ADAMA']
# for x in adama:
#    print [y['item_id'] for y in x['items']]
#    .....:
# [u'00964ITE']
# [u'00168ITE']
# [u'00185ITE']
# [u'00965ITE']
# [u'00159ITE']
# [u'01024ITE']
# [u'01024ITE', u'00997ITE']
# [u'01024ITE', u'00997ITE']

# NO PAYMENT INFO SHOWING

def get_event(gs_ep_data):
	"""
	Get the event from the data imported from GoShow
	:gs_ep_data [<dict>] json.load data from goshow report
	:return {event_code: '', event_subcode:'', description:''}
	"""
	results = {'event_code': '', 'event_subcode':'', 'description':''}
	# 	[{"event_id": "CAMFHILLCODETR",
	#  "event": "Camfour\/Hill Country 2016 Dealer Trade Show",
	#  "event_startdate": "01-10-2016",}]
	event = gs_ep_data[0]
	results['event_code']    = event.get('event_id')
	results['event_subcode'] = format_goshow_date(event.get('event_startdate'), 0)
	results['description']   = event.get('event')
	return results

def get_customer_info(customer):
	"""Get a customers info from an orders node
	   :customer <tuple> one node from sort_by_customer results
	"""
	c = customer[1][0]
	return{
		"customer": c.get('customer'),
		"bill_to": c.get('bill_to'),
		"ship_to": c.get('ship_to'),
		"booth_number": c.get('booth_number'),
		"taxable": c.get('taxable'),
		'order_date': c.get('order_date')
	}

def get_customer_orders(customer):
	"""
	Loop over the results of sort_by_customer and create a list of the orders
	:customer <tuple> one node from sort_by_customer results
	"""
	results = []	
	for order in customer[1]:
		results.append({
			"id": order.get("id"),
			"order_date": order.get("order_date"),
			"sales_person": order.get("sales_person"),
			"items": order.get('items'),
			"payments": order.get('payments')
		})
	return results

def merge_orders(customer):
	"""
	Merge orders by order id
	GoShow list orders with multipule items twice.
	This will merge those into one order
	:customer <tuple> one node from sort_by_customer results
	"""
	obj = {}
	for order in sorted(customer['orders'], key=lambda k: k['id']):
		order_id = order.get('id')
		if not obj.has_key(order_id):
			obj[order_id] = order
	return obj

def merge_items(customer):
	""" 
	Merge all the items for an exhibitor into one item list
	:customer <tuple> one node from sort_by_customer results
	"""
	results = []
	
	for x in customer['orders']:
		# remove empty items
		for item in x['items']:				
			if item.get('Item name') and item.get("item_id"):
				item['order_id'] = x['id']
				results.append(item) 

	return results


def merge_payments(customer):
	order_ids = []
	pmts = {}
	for items in customer['orders']:
		order_id = items['id']
		if not order_id in order_ids:
			order_ids.append(order_id)
			payment = items['payments'][0]
			payment_id = payment['payment_id']
			paid_amount = float(payment['paid_amount'])
			if payment['number'] == 'NA' and paid_amount == 0.0:
				#  import ipdb; ipdb.set_trace()
				continue
			if not payment_id in pmts:
				pmts[payment_id] = payment
				pmts[payment_id]['paid_amount'] = paid_amount
			else:
				pmts[payment_id]['paid_amount'] = pmts[payment_id]['paid_amount'] + paid_amount
	return pmts

# def merge_payments(customer):
# 	"""
# 	Merge all the payments for an exhibitor into one payment list
# 	GoShow will break out payments by work order, 
# 	this will merge and total payments with the same id
# 	:customer <tuple> one node from sort_by_customer results
# 	"""
# 	# get all the payment info from the order
# 	payments = [p['payments'] for p in customer['orders']]
# 	results = {}
# 	for payment in payments:
# 		for trx in payment:			
# 			payment_id = trx.get('payment_id')
# 			# no payment_id no payment?
# 			if not payment_id:
# 				continue
# 			paid_amount = float(trx.get('paid_amount'))			
# 			if not results.has_key(payment_id):				
# 				results[payment_id] = trx
# 				results[payment_id]['paid_amount'] = paid_amount	
# 				continue
# 			results[payment_id]['paid_amount'] += paid_amount
# 	return results.values()
# 	# customer['payments'] = results.values()
# 	# return customer

def reorg_customer_data(customer_orders):
	"""
	Reorganize customer's data to something more comprehensiable for EventPath
	:customer_orders [(customer name, [customer data])] results of sort_by_customer
	"""
	results = []
	for customer in customer_orders:
		c = get_customer_info(customer)
		c['orders'] = get_customer_orders(customer)
		# merge_payments and merge_items
		# needs orders added to c before it can do it's things
		c['payments'] = merge_payments(c)
		c['items'] = merge_items(c)
		results.append(c)
	return results

def sort_by_customer(customer_data):	
	""" 
	Sort GoShow's EventPath report by customer
	Sorts by customers name and booth_number
	:customer_data [(customer name, customer data)] Deserialized GoShow EventPath Report
	:returns customers_orders 
	"""
	# get all the orders in the event
	orders = customer_data[0]['orders']
	# group orders by customer name
	customers = set((x['customer'], x['booth_number']) for x in orders)
	customer_orders = []

	for name, booth in customers:
		customer_orders.append(
			(name, [x for x in orders if x['customer'] == name and x['booth_number'] == booth])
		)

	return customer_orders				

def main(gs_ep_data):
	""" 
	Take in data from GoShow's eventpath json report and arrange
	by customer.
	Each node will equal a slstrx in EventPath
	:gs_ep_data [<dict>] json.load data from goshow report
	:return [<dict>]
	"""
	results = None
	customers = sort_by_customer(gs_ep_data)
	results = reorg_customer_data(customers)
	return results

# def stuff(entry):
# 	customers = sort_by_customer(entry)
# 	results = []
# 	import ipdb; ipdb.set_trace()
# 	for customer in customers:
# 		cust
# 		 = get_customer_info(customer)
# 		cust['orders'] = get_customer_orders(customer)
# 		cust['payments'] = merge_payments(cust)
# 		cust['items'] = merge_items(cust)
# 		results.append(cust)
# 	return results	
# import json
# nela = json.load(open('../data/eventorders/nela/nela.json', 'r'))
# nela_reorg_orders = main(nela)
