from jsonfield import JSONField
from django.db import models

class Entry(models.Model):
	created  = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified = models.DateTimeField('', auto_now=True, auto_now_add=False)
	data     = JSONField('Entry Data')
	success  = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.created)

	class Meta:
		verbose_name_plural = "Entries"

# class Trx(models.Model):
# 	entry = models.ForeignKey(Entry, related_name="transactions")

class Event(models.Model):
	event_code    = models.CharField("Event Code", max_length=255, blank=True)
	event_subcode = models.CharField("Event Subcode", max_length=255, blank=True)
	description   = models.CharField("Description", max_length=255, blank=True)

	def __unicode__(self):
		return "%s - %s" % (self.event_code, self.event_subcode)

class Order(models.Model):
	
	ep_id = models.CharField("EP Order Number", max_length=255, blank=True)
	gs_id = models.CharField("GS Order ID", max_length=255, blank=True)
	in_ep = models.BooleanField('Data in EventPath', default=False)

	batch_name = models.CharField("Batch Name", max_length=255, blank=True)

	place_code           = models.CharField("Place Code", max_length=255, blank=True)
	description          = models.CharField("Description", max_length=255, blank=True)
	primary_address_code = models.CharField("Primary Address Code", max_length=255, blank=True, default="BILLTO")
	ship_to_address      = models.CharField("Ship To Address", max_length=255, blank=True, default="SHIPTO")
	bill_to_address      = models.CharField("Bill To Address", max_length=255, blank=True, default="BILLTO")
	taxable              = models.BooleanField("Taxable", default=True)
	booth_number         = models.CharField("Booth", max_length=255, blank=True)	
	order_date           = models.CharField("Order Date", max_length=255, blank=True)
	sales_person         = models.CharField("Sales Person", max_length=255, blank=True)
	note                 = models.TextField("Notes", blank=True)

	event = models.ForeignKey(Event, related_name="orders")
	entries = models.ManyToManyField(Entry, related_name="orders")

	created  = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified = models.DateTimeField('', auto_now=True, auto_now_add=False)

	def __unicode__(self):
		if self.ep_id:
			return self.ep_id
		return self.place_code

	def create_customer_address(self, address_info, address_code):
		
		_obj              = CustomerAddress()
		_obj.address_code = address_code
		_obj.place_code   = self
		_obj.name         = address_info.get('name', '')
		_obj.contact      = address_info.get('name', '')
		_obj.address1     = address_info.get('address', '')
		_obj.address2     = ''
		_obj.city         = address_info.get('city', '')
		_obj._state       = address_info.get('state', '')
		_obj.zip          = address_info.get('')
		_obj.country      = address_info.get('country', '')
		_obj.phone1       = ''
		_obj.phone2       = ''
		_obj.fax          = ''
		_obj.email        = ''
		_obj.save()

class CustomerAddress(models.Model): 
	name = models.CharField(max_length=255, blank=True)
	place_code   = models.ForeignKey(Order, related_name="addresses")
	address_code = models.CharField(max_length=255)	
	contact      = models.CharField(max_length=255, blank=True)
	address1     = models.CharField(max_length=255, blank=True)
	address2     = models.CharField(max_length=255, blank=True)
	city         = models.CharField(max_length=255, blank=True)
	state        = models.CharField(max_length=255, blank=True)
	zip          = models.CharField(max_length=255, blank=True)
	country      = models.CharField(max_length=255, blank=True)
	phone1       = models.CharField(max_length=255, blank=True)
	phone2       = models.CharField(max_length=255, blank=True)
	fax          = models.CharField(max_length=255, blank=True)
	email        = models.CharField(max_length=255, blank=True)

	def __unicode__(self):
		return "%s - %s" % (self.place_code.place_code, self.address_code)

class OrderItem(models.Model):
	
	gs_id          = models.CharField("GS Workorder ID", max_length=255, blank=True)
	ep_id          = models.CharField("EP LineItem ID", max_length=255, default=0)
	in_ep          = models.BooleanField('Data in EventPath', default=False)
	
	# event path item number
	item_number = models.CharField("EventPath Item Number", max_length=255, blank=True)
	# gs item id and gs name
	gs_item_id     = models.CharField("GS Item ID", max_length=255, blank=True)
	item_name      = models.CharField("Item Name", max_length=255, blank=True)
	# list of attributes that came in from order
	# options        = models.CharField("GS Options", max_length=255, blank=True)
	options        = JSONField("GS Options")
	# line item info from gs
	unit_price     = models.DecimalField("Unit Price", max_digits=10, decimal_places=2, blank=True)
	qty            = models.DecimalField("Quantity", max_digits=8, decimal_places=3, blank=True)
	tax_total      = models.DecimalField("Total Tax", max_digits=10, decimal_places=2, blank=True)
	taxable        = models.BooleanField("Taxable", default=True)
	line_total     = models.DecimalField("Line Total", max_digits=10, decimal_places=2, blank=True)
	notes          = models.TextField("Notes", blank=True)
	
	order = models.ForeignKey(Order, related_name="items")
	
	def __unicode__(self):
		return "%s" % self.ep_id

class CardTypeInvalidException(Exception): pass

class OrderPayment(models.Model):

	# CASH       = 0
	# CHECK      = 1
	# MASTERCARD = 2
	# VISA       = 2
	# DISCOVER   = 2
	# DINNERS    = 3
	# AMEX       = 3

	gs_id = models.CharField("GS Payment ID", max_length=255, blank=True)
	ep_id = models.CharField("EP Payment Number", max_length=255, blank=True)

	in_ep = models.BooleanField('Data in EventPath', default=False)
	# payment_id = models.CharField(max_length=255, blank=True)
	# payment_number = models.CharField(max_length=255, blank=True)

	payment_type       = models.IntegerField("Payment Type", default=0)
	payment_amount     = models.DecimalField("Paid Amount", max_digits=10, decimal_places=2, blank=True)
	payment_date       = models.CharField("Payment Date", max_length=255, blank=True)
	check_number       = models.CharField("Check Number", max_length=255, blank=True)
	credit_card_id     = models.CharField("Credit Card ID", max_length=255, blank=True)
	credit_card_number = models.CharField("Credit Card Number", max_length=255, blank=True)
	
	authorization_code = models.CharField("Auth Code", max_length=255, blank=True)
	expiration_date    = models.CharField("Expire Date", max_length=255, blank=True)

	created  = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified = models.DateTimeField('', auto_now=True, auto_now_add=False)	

	notes          = models.TextField("Notes", blank=True)

	order = models.ForeignKey(Order, related_name="payments")	

	def __unicode__(self):
		return self.ep_id

	def get_ep_payment_type(self, payment):

		payment_type = payment.get('payment_type').lower()
		
		if payment_type in ['credit', 'credit card']:
			# what if no card type?
			try:
				card_type = payment.get('credit_card_type').lower()
			except CardTypeInvalidException, e:
				raise e
				
			if card_type:
				if card_type in ['diners', 'amex']:
					return 3
				else:
					return 2
		if payment_type == 'check':
			return 1

		if payment_type == 'cash':
			return 0
		return 0	


