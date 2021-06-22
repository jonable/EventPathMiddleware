import json
from .models import Order, Event, Entry, OrderItem, OrderPayment
from .epformats import (
	get_ep_payment_type, format_goshow_date, 
	create_customer_code, get_ep_card_id, get_ep_country_code
)
from .parse_gs_json import main as parse_event_orders
from .parse_gs_json import get_event

from .models import CustomerAddress
def create_customer_address(order, address_info, address_code):
	"""
	Create a new customer address for an order
	:order <entries2.models.Order>
	:address_info <dict> User Address Info
	:address_code <string> SHIPTO or BILLTO
	:return <entries2.models.CustomerAddress>
	"""
	_obj              = CustomerAddress(place_code=order)
	_obj.address_code = address_code
	_obj.name         = address_info.get('name') or ''
	_obj.contact      = address_info.get('name') or ''
	_obj.address1     = address_info.get('address') or ''
	_obj.address2     = ''
	_obj.city         = address_info.get('city') or ''
	_obj.state        = address_info.get('state') or ''
	_obj.zip          = '' # address_info.get('')
	_obj.country      = get_ep_country_code(address_info.get('country') or '')
	_obj.phone1       = ''
	_obj.phone2       = ''
	_obj.fax          = ''
	_obj.email        = ''
	_obj.save()
	return _obj

def item_is_taxable(item):
	"""
	Check if an incoming item is taxable
	:item <dict> 
	:return <bool>
	"""
	total_tax = item.get('tax_total')
	if type(total_tax) == str:
		return bool(float(total_tax))
	else:
		return bool(total_tax)

from mappings.utils import map_item
def get_ep_item_number(item):	
	gs_item_name = item.get('Item name')
	options      = item.get('options')
	return map_item(gs_item_name, options=options)

def add_order_items(order, customer_data):
	""" 
	Add items to an order.
	Clears old items and re-adds all items
	:order <entries2.models.Order>
	:customer_data [{'items': []}]
	:return [ids] added item ids
	"""
	results = []
	if order.items.exists():
		order.items.all().delete()
	
	for item in customer_data.get('items'):
		item_obj = OrderItem(order=order)
		item_number = get_ep_item_number(item)

		gs_id      = item.get('order_id')
		qty        = item.get('qty', 0.000)
		unit_price = item.get('unit_price', 0.00)
		taxable    = item_is_taxable(item)
		tax_total  = item.get('tax_total', 0.00)
		line_total = item.get('line_total', 0.00)
		gs_item_id = item.get('item_id')
		item_name  = item.get('Item name')
		# options    = ", ".join(["%s: %s" % (x[0], x[1]) for x in item.get('options')])
		options    = item.get('options')
		item_obj.gs_id      = gs_id
		item_obj.qty        = qty
		item_obj.unit_price = unit_price
		item_obj.taxable    = taxable
		item_obj.tax_total  = tax_total
		item_obj.gs_item_id = gs_item_id
		item_obj.item_name  = item_name
		item_obj.options    = options
		item_obj.ep_id      = item_number
		item_obj.line_total = line_total
		item_obj.save()		
		# item_obj, created = OrderItem.objects.get_or_create()
		results.append(item_obj.id)

	return results

def add_order_payments(order, customer_data):
	""" 
	Add payments to an order
	Ignores existing payments (searches on GS's payment_id)
	:order <entries2.models.Order>
	:customer_data [{'items': []}]
	:return [ids] added payment ids
	"""
	results = []
	for payment in customer_data.get('payments'):
		# check if payment already exists, if so skip this payment
		payment_objs = OrderPayment.objects.filter(order=order, gs_id=payment.get('payment_id'))
		if payment_objs:
			continue
		# create a new orderpayment object
		payment_obj = OrderPayment(order=order, gs_id=payment.get('payment_id'))
		# get the EP payment type
		payment_type   = get_ep_payment_type(payment)
		# get the paid amount and payment date
		payment_amount = payment.get('paid_amount')
		payment_date   = format_goshow_date(payment.get('payment_date'), 2)

		# check payment type and set the correct info
		if payment_type in [2,3]:
			# credit card
			payment_obj.credit_card_id = get_ep_card_id(payment.get("credit_card_type"))
			payment_obj.credit_card_number = payment.get('number')			
		elif payment_type == 1:
			# check
			# not sure if number is also check number...
			payment_obj.check_number = payment.get('number')
		else:
			# cash
			pass

		payment_obj.payment_type   = payment_type
		payment_obj.payment_amount = payment_amount
		payment_obj.payment_date   = payment_date

		payment_obj.save()
		results.append(payment_obj.gs_id)
	return results

def check_import_event(event_code, event_subcode, event_orders_json):
	"""
	Ensure the importing orders are for the correct event
	:event_code <string> EventPath Event EventCode
	:event_subcode <string> EventPath Event Subcode
	:event_orders_json <string> file path to GS's "EventPath JSON File Report"
	:return <bool>
	"""
	event_orders = json.load(open(event_orders_json, 'r'))
	event = get_event(event_orders)
	import ipdb; ipdb.set_trace()
	if event_code == event.get('event_code') and event.get('event_subcode') in event_subcode:
		return True
	return False

def update_order(event_code, event_subcode, event_orders_json):
	""" 
	Perform a GS->EP update, using data from GS's "EventPath JSON File Report"
	https://ser.goshowonline.com/reports/eventpath
	:event_code <string> EventPath Event EventCode
	:event_subcode <string> EventPath Event Subcode
	:event_orders_json <string> file path to GS's "EventPath JSON File Report"
	:reutrn [[(order ids, order created)], <entries2.models.Entry>]
	"""
	results = []
	event_orders = json.load(open(event_orders_json, 'r'))
	customers = parse_event_orders(event_orders)

	# get the event
	event, event_created = Event.objects.get_or_create(event_code=event_code, event_subcode=event_subcode)

	entry = Entry.objects.create(data=event_orders)

	for customer in customers:
		customer_name = customer.get('customer')
		booth_number  = customer.get('booth_number')
		place_code    = create_customer_code(customer_name)
		# check if an order already exists
		# an order exist if event, place_code and booth_number are matched in the db
		# GS creates orders for each wo, we are creating one order per exhibitor... so this is it.
		order_obj, order_created = Order.objects.get_or_create(event=event, place_code=place_code, booth_number=booth_number)

		if order_created:
			order_obj.description  = customer_name
			order_obj.sales_person = customer.get('sales_person', '')
			order_obj.order_date   = format_goshow_date(customer.get('order_date'), 1)
			order_obj.batch_name   = event.event_code
			order_obj.save()
		# if the order has no addresses attached, set them
		if not order_obj.addresses.exists():
			create_customer_address(order_obj, customer.get('ship_to'), "SHIPTO")
			create_customer_address(order_obj, customer.get('bill_to'), "BILLTO")
			if order_created:
				order_obj.bill_to_address = "BILLTO"
				order_obj.ship_to_address = "SHIPTO"
				order_obj.primary_address_code = "BILLTO"
			order_obj.save()

		items    = add_order_items(order_obj, customer)
		payments = add_order_payments(order_obj,customer)		
		order_obj.entries.add(entry)
		results.append((order_obj.id, order_created))

	return results, entry


def order_update_note(datestamp):
	return "Order updated by GStoEP on %s" % datestamp.strftime('%Y-%m-%d %H:%M')
def order_created_note(datestamp):
	return "Order created by GStoEP on %s" % datestamp.strftime('%Y-%m-%d %H:%M')

from django.conf import settings 
# import win32com.client
def load_com():	
	return {} # win32com.client.Dispatch(settings.EPCOM_NAME)

def import_to_eventpath(entry):
	
	com = load_com()

	for order in entry.orders.all():
		# set the event		
		com.SetEvent(order.event.event_code, order.event.event_subcode)
		note = order.note
		# check for customer create if none
		if not com.CustomerExists(order.place_code):
			com.CreateCustomer(order.place_code, order.description)
			assert(com.CustomerExists(order.place_code))
			for address in order.addresses.all():
				place_code   = order.place_code
				address_code = address.address_code
				contact      = address.contact
				address1     = address.address1
				address2     = address.address2
				city         = address.city
				_state       = address.state
				_zip         = address.zip
				country      = address.country
				phone1       = address.phone1
				phone2       = address.phone2
				fax          = address.fax
				email        = address.email
				is_primary   = False
				if all([contact, address1, city, _state, _zip]):
					com.CreateAddress(
						address_code, contact, address1,
						address2, city, _state,
						_zip, country, phone1,
						phone2, fax, email, is_primary
					)		 	
		# unsure if i'm going to user in_ep
		# either way, no ep_id create order
		if not order.ep_id or not order.in_ep:
			batch_name    = order.event.event_code
			booth_number  = order.booth_number
			order_date    = order.order_date
			customer_code = order.place_code
			bill_to_code  = order.bill_to_address # 'BILLTO' # order.addresses.filter(address_code='BILLTO')
			ship_to_code  = order.ship_to_address # 'SHIPTO'
			note = order_created_note(entry.created)
			com.CreateOrder(
				batch_name, booth_number, customer_code, 
				bill_to_code, ship_to_code, order_date, note
			)
			order.ep_id = com.OrderNumber
			order.in_ep = True
			order.save()
		else:
			com.OrderNumber = order.ep_id
		assert(com.OrderNumber)
		# set items on ep order
		# I may need to rethink this part.
		# On the surface it totally works, 
		# clear items and readd them to the order in eventpath
		# this ensure any update is covered 
		# items = [(item_number), qty, unit_price, tax, note)]
		items = []
		for item in order.items.all():
			item_number = item.item_number
			qty         = item.qty
			unit_price  = item.unit_price

			# ????
			# line_total  = item.line_total
			
			taxable     = item.taxable
			notes       = item.notes
			# if not epitem_exists(item_number)
			# report...
			items.append((
				item_number, qty, unit_price, taxable, notes
			))
		if items:
			# AddItems(items, over write existing items)
			com.AddItems(items, True)

		# set payments
		# What about voided payments, refunds, ect?
		for payment in order.payments.all():
			if not payment.ep_id and not payment.in_ep:
				payment_amount     = payment.payment_amount
				payment_date       = payment.payment_date
				payment_type       = payment.payment_type
				check_number       = payment.check_number
				credit_card_id     = payment.credit_card_id
				credit_card_number = payment.credit_card_number
				authorization_code = payment.authorization_code
				expiration_date    = payment.expiration_date
				
				com.AddPayment(payment_amount, payment_date, check_number, 
					credit_card_id, credit_card_number, authorization_code, 
					expiration_date, payment_type)
		
				payment.ep_id = com.PaymentNumber
				payment.in_ep = True
				payment.save()

		if order.note != note:
			com.UpdateOrder(order.note)
		else:
			com.UpdateOrder('')

import decimal
def decimal_default(obj):
	if isinstance(obj, decimal.Decimal):
		return float(obj)
	raise TypeError

def serialize_entry(entry):
	
	# com = load_com()
	_entry = []
	for order in entry.orders.all():
		_order = {}
		# set the event		
		_order['event'] = (order.event.event_code, order.event.event_subcode)
		# note = order.note
		# check for customer create if none
		
		_order['customer'] = (order.place_code, order.description)
		_order['address'] = {}
		for address in order.addresses.all():
			_order['address'][address.address_code] = dict(
				place_code   = order.place_code,
				address_code = address.address_code,
				contact      = address.contact,
				address1     = address.address1,
				address2     = address.address2,
				city         = address.city,
				_state       = address.state,
				_zip         = address.zip,
				country      = address.country,
				phone1       = address.phone1,
				phone2       = address.phone2,
				fax          = address.fax,
				email        = address.email,
				is_primary   = False
			)

			
		# unsure if i'm going to user in_ep
		# either way, no ep_id create order
		if not order.ep_id or not order.in_ep:
			_order.update(dict(
				batch_name    = order.event.event_code,
				booth_number  = order.booth_number,
				order_date    = order.order_date,
				customer_code = order.place_code,
				bill_to_code  = order.bill_to_address, # 'BILLTO' # order.addresses.filter(address_code='BILLTO'),
				ship_to_code  = order.ship_to_address, # 'SHIPTO',
				note = order_created_note(entry.created),
			))
			# com.CreateOrder(
			# 	batch_name, booth_number, customer_code, 
			# 	bill_to_code, ship_to_code, order_date, note
			# )
			# order.ep_id = com.OrderNumber
			# order.in_ep = True
			# order.save()
		# else:
		# 	com.OrderNumber = order.ep_id
		# assert(com.OrderNumber)
		# set items on ep order
		# I may need to rethink this part.
		# On the surface it totally works, 
		# clear items and readd them to the order in eventpath
		# this ensure any update is covered 
		# items = [(item_number), qty, unit_price, tax, note)]
		items = []
		for item in order.items.all():
			item_number = item.item_number
			qty         = item.qty
			unit_price  = item.unit_price
			line_total  = item.line_total
			taxable     = item.taxable
			notes       = item.notes
			# if not epitem_exists(item_number)
			# report...
			items.append((
				item_number, qty, unit_price, line_total, taxable, notes
			))
		if items:
			# AddItems(items, over write existing items)
			# com.AddItems(items, True)
			_order['items'] = items
		
		# set payments
		# What about voided payments, refunds, ect?
		_order['payments'] = {}
		for payment in order.payments.all():
			if not payment.ep_id and not payment.in_ep:
				_order['payments'][payment.gs_id] = dict(
					payment_amount     = payment.payment_amount,
					payment_date       = payment.payment_date,
					payment_type       = payment.payment_type,
					check_number       = payment.check_number,
					credit_card_id     = payment.credit_card_id,
					credit_card_number = payment.credit_card_number,
					authorization_code = payment.authorization_code,
					expiration_date    = payment.expiration_date,
				)
				# com.AddPayment(payment_amount, payment_date, check_number, 
				# 	credit_card_id, credit_card_number, authorization_code, 
				# 	expiration_date, payment_type)
		
				# payment.ep_id = com.PaymentNumber
				# payment.in_ep = True
				# payment.save()

		# if order.note != note:
		# 	com.UpdateOrder(order.note)
		# else:
		# 	com.UpdateOrder('')
		_entry.append(_order)
	return _entry

# import win32com.client
# def load_com():	
# 	return win32com.client.Dispatch('EPCOM.EPDataModule')

def import_to_eventpath2(entry):
	
	com = load_com()

	for order in entry:
		# set the event		
		com.SetEvent(order['event'][0], order['event'][1])
		note = order['note']
		# check for customer create if none
		if not com.CustomerExists(order['customer_code']):
			com.CreateCustomer(order['customer_code'], order['customer'][1])
			assert(com.CustomerExists(order['customer_code']))		
			
			for address in order['address'].values():
				place_code     = order['place_code']
				address_code = address['address_code']
				contact      = address['contact']
				address1     = address['address1']
				address2     = address['address2']
				city         = address['city']
				_state       = address['_state']
				_zip         = address['_zip']
				country      = address['country']
				phone1       = address['phone1']
				phone2       = address['phone2']
				fax          = address['fax']
				email        = address['email']
				is_primary   = address['is_primary']

				com.CreateAddress(
					address_code, contact, address1,
					address2, city, _state,
					_zip, country, phone1,
					phone2, fax, email, is_primary
				)		 	
		
		# unsure if i'm going to user in_ep
		# either way, no ep_id create order
		# if not order.ep_id or not order.in_ep:
		batch_name    = order['event'][0]
		booth_number  = order['booth_number']
		order_date    = order['order_date']
		customer_code = order['place_code']
		bill_to_code  = order['bill_to_address'] # 'BILLTO' # order.addresses.filter(address_code='BILLTO')
		ship_to_code  = order['ship_to_address'] # 'SHIPTO'
		note = order_created_note(entry.created)
			
		com.CreateOrder(
			batch_name, booth_number, customer_code, 
			bill_to_code, ship_to_code, order_date, note
		)

		order['ep_id'] = com.OrderNumber

		# else:
		# 	com.OrderNumber = order.ep_id
		assert(com.OrderNumber)
		# set items on ep order
		# I may need to rethink this part.
		# On the surface it totally works, 
		# clear items and readd them to the order in eventpath
		# this ensure any update is covered 
		# items = [(item_number), qty, unit_price, tax, note)]
		# items = []
		# for item in order['items']:
		# 	item_number = item.item_number
		# 	qty         = item.qty
		# 	unit_price  = item.unit_price
		# 	taxable     = item.taxable
		# 	notes       = item.notes
		# 	# if not epitem_exists(item_number)
		# 	# report...
		# 	items.append((
		# 		item_number, qty, unit_price, taxable, notes
		# 	))
		# if items:
		# 	# AddItems(items, over write existing items)
		# 	com.AddItems(items, True)

		com.AddItems(order['items'], True)

		# set payments
		# What about voided payments, refunds, ect?
		for payment in order['payments'].values():

			payment_amount     = payment['payment_amount']
			payment_date       = payment['payment_date']
			payment_type       = payment['payment_type']
			check_number       = payment['check_number']
			credit_card_id     = payment['credit_card_id']
			credit_card_number = payment['credit_card_number']
			authorization_code = payment['authorization_code']
			expiration_date    = payment['expiration_date']
			
			com.AddPayment(payment_amount, payment_date, check_number, 
				credit_card_id, credit_card_number, authorization_code, 
				expiration_date, payment_type)
		
			payment['ep_id'] = com.PaymentNumber

		if order['note'] != note:
			com.UpdateOrder(order['note'])
		else:
			com.UpdateOrder('')	

	return entry

def import_to_eventpath2_updates(entry):
	
	com = load_com()

	for order in entry:
		# set the event		
		com.SetEvent(order['event'][0], order['event'][1])
		note = order['note']

		# check if order is in EP
		# if not com.OrderExists(order['ep_id']):
		if not order['ep_id']:
			# check for customer create if none
			if not com.CustomerExists(order['customer_code']):
				com.CreateCustomer(order['customer_code'], order['customer'][1])
				assert(com.CustomerExists(order['customer_code']))		
				
				for address in order['address'].values():				
					place_code     = order['place_code']
					address_code = address['address_code']
					contact      = address['contact']
					address1     = address['address1']
					address2     = address['address2']
					city         = address['city']
					_state       = address['_state']
					_zip         = address['_zip']
					country      = address['country']
					phone1       = address['phone1']
					phone2       = address['phone2']
					fax          = address['fax']
					email        = address['email']
					is_primary   = address['is_primary']

					com.CreateAddress(
						address_code, contact, address1,
						address2, city, _state,
						_zip, country, phone1,
						phone2, fax, email, is_primary
					)		 	
			
			# unsure if i'm going to user in_ep
			# either way, no ep_id create order
			# if not order.ep_id or not order.in_ep:
			batch_name    = order['event'][0]
			booth_number  = order['booth_number']
			order_date    = order['order_date']
			customer_code = order['place_code']
			bill_to_code  = order['bill_to_address'] # 'BILLTO' # order.addresses.filter(address_code='BILLTO')
			ship_to_code  = order['ship_to_address'] # 'SHIPTO'
			note = order_created_note(entry.created)
				
			com.CreateOrder(
				batch_name, booth_number, customer_code, 
				bill_to_code, ship_to_code, order_date, note
			)

			order['ep_id'] = com.OrderNumber

		else:
			com.OrderNumber = order.ep_id
		assert(com.OrderNumber)
		# set items on ep order
		# I may need to rethink this part.
		# On the surface it totally works, 
		# clear items and readd them to the order in eventpath
		# this ensure any update is covered 
		# items = [(item_number), qty, unit_price, tax, note)]
		# items = []
		# for item in order['items']:
		# 	item_number = item.item_number
		# 	qty         = item.qty
		# 	unit_price  = item.unit_price
		# 	taxable     = item.taxable
		# 	notes       = item.notes
		# 	# if not epitem_exists(item_number)
		# 	# report...
		# 	items.append((
		# 		item_number, qty, unit_price, taxable, notes
		# 	))
		# if items:
		# 	# AddItems(items, over write existing items)
		# 	com.AddItems(items, True)

		com.AddItems(order['items'], True)

		# set payments
		# What about voided payments, refunds, ect?
		for payment in order['payments'].values():
			# com.CheckPaymentExist(payment['ep_id'])...
			if not payment['ep_id']:
				payment_amount     = payment['payment_amount']
				payment_date       = payment['payment_date']
				payment_type       = payment['payment_type']
				check_number       = payment['check_number']
				credit_card_id     = payment['credit_card_id']
				credit_card_number = payment['credit_card_number']
				authorization_code = payment['authorization_code']
				expiration_date    = payment['expiration_date']
				
				com.AddPayment(payment_amount, payment_date, check_number, 
					credit_card_id, credit_card_number, authorization_code, 
					expiration_date, payment_type)
			
				payment['ep_id'] = com.PaymentNumber

		if order['note'] != note:
			com.UpdateOrder(order['note'])
		else:
			com.UpdateOrder('')	

	return entry