import time, datetime, os
import xlwt

styles = dict(
    bold = 'font: bold 1',
    italic = 'font: italic 1',
    # Wrap text in the cell
    wrap_bold = 'font: bold 1; align: wrap 1;',
    # White text on a blue background
    reversed = 'pattern: pattern solid, fore_color blue; font: color white;',
    # Light orange checkered background
    light_orange_bg = 'pattern: pattern fine_dots, fore_color white, back_color orange;',
    # Heavy borders
    bordered = 'border: top thick, right thick, bottom thick, left thick;',
    # 16 pt red text
    big_red = 'font: height 320, color red;',
)

def write_header(ws, current_row, row, style):
	derp = {
		'line_items': [
			'ItemNumber',
			'Qty',
			'UnitPrice',
			'Taxable'
		], 
		'order': [
			'CustomerCode',
			'BoothNumber',
			'OrderDate',
			'BatchName',
			'OrderNote'
		], 
		'payments': [
			'PaymentDate',
			'AuthCode',
			'ExpireDate',
			'CCNumber',
			'PaymentAmount',
			'PaymentType',
			'CCID',
			'CheckNumber'
		]
	}

	for i, herp in enumerate(derp[row]):
		ws.write(current_row, i+1, herp, style)

def excel_report(entries):
	event = entries[0].get('event')
	event_code = event[0]
	timestamp = str(int(time.time()))
	datestamp = datetime.datetime.now()
	filename = "%s-%s.xls" % (event_code, timestamp)

	xf_bold = xlwt.easyxf('font: bold 1')
	xf_large_bold = xlwt.easyxf('font: bold 1, height 400')
	xf_italic = xlwt.easyxf('font: italic 1')

	workbook = xlwt.Workbook()
	ws = workbook.add_sheet('event_code')

	ws.col(1).width = 256 * 20
	# ws.col(1).width = 256 * 20
	# first_col.width = 256 * 20              # 20 characters wide (-ish)

	# ws.write(0, i, field)
	# ws.write(0,0, "Entries Report", xf_large_bold)
	ws.write_merge(0, 0, 0, 3, label="Entries Report", style=xf_large_bold)
	ws.write(1,0, "date: ")
	ws.write(1,1, str(datestamp))
	ws.write(2,0, "Event: ")
	ws.write(2,1, "%s - %s" % (event[0], event[1]))	

	current_row = 4
	# import ipdb; ipdb.set_trace()
	for entry in entries:
		# if entry.get('event') != event_code:
		# 	continue
		doc_number    = entry.get("ep_id")
		customer_code = entry.get('customer_code')
		booth_number  = entry.get('booth_number')
		order_date    = entry.get('order_date')		
		batch_name    = entry.get('batch_name')
		note          = entry.get('note')

		ws.write(current_row, 1, "DocNumber: ", xf_bold)
		ws.write_merge(current_row, current_row, 2, 3, label=doc_number)		
		current_row += 1
		write_header(ws, current_row, 'order', xf_italic)
		current_row += 1
		ws.write(current_row, 1, customer_code)
		ws.write(current_row, 2, booth_number)
		ws.write(current_row, 3, order_date)
		ws.write(current_row, 4, batch_name)
		ws.write(current_row, 5, note)
		current_row += 1
		
		# items
		ws.write(current_row, 1, "Line Items", xf_bold)
		current_row += 1
		write_header(ws, current_row, 'line_items', xf_italic)
		current_row += 1
		for item in entry.get("items"):
			for i, derp in enumerate(item):
				ws.write(current_row, i+1, str(derp))
			current_row += 1
		
		ws.write(current_row, 1, "Payments", xf_bold)
		current_row += 1	
		write_header(ws, current_row, 'payments', xf_italic)
		current_row += 1
		# payments
		for key, value in entry.get('payments').items():
			payment_date       = value.get("payment_date")                
			authorization_code = value.get("authorization_code")    
			expiration_date    = value.get("expiration_date")          
			credit_card_number = value.get("credit_card_number")    
			payment_amount     = value.get("payment_amount")            
			payment_type       = value.get("payment_type")                
			credit_card_id     = value.get("credit_card_id")            
			check_number       = value.get("check_number")	

			ws.write(current_row, 1,payment_date)
			ws.write(current_row, 2,authorization_code)
			ws.write(current_row, 3,expiration_date)
			ws.write(current_row, 4,credit_card_number)
			ws.write(current_row, 5,payment_amount)
			ws.write(current_row, 6,payment_type)
			ws.write(current_row, 7,credit_card_id)
			ws.write(current_row, 8,check_number)				
			ws.write(current_row, 9, "gs-id: %s" % key)
			current_row += 1

		current_row += 2	
	
	workbook.save(os.path.join(os.path.abspath('./reports'), filename))

def excel_report2(entry_obj):
	
	orders = entry_obj.orders.all()
	event = orders.first().event
	# event = entries[0].get('event')
	event_code = event.event_code
	timestamp = str(int(time.time()))
	datestamp = datetime.datetime.now()
	filename = "%s-%s.xls" % (event_code, timestamp)

	xf_bold = xlwt.easyxf('font: bold 1')
	xf_large_bold = xlwt.easyxf('font: bold 1, height 400')
	xf_italic = xlwt.easyxf('font: italic 1')

	workbook = xlwt.Workbook()
	ws = workbook.add_sheet('event_code')

	ws.col(1).width = 256 * 20
	# ws.col(1).width = 256 * 20
	# first_col.width = 256 * 20              # 20 characters wide (-ish)

	# ws.write(0, i, field)
	# ws.write(0,0, "Entries Report", xf_large_bold)
	ws.write_merge(0, 0, 0, 3, label="Entries Report", style=xf_large_bold)
	ws.write(1,0, "date: ")
	ws.write(1,1, str(datestamp))
	ws.write(2,0, "Event: ")
	ws.write(2,1, "%s - %s" % (event.event_code, event.event_subcode))	

	current_row = 4
	# import ipdb; ipdb.set_trace()
	for order in orders:
		# if entry.get('event') != event_code:
		# 	continue
		doc_number    = order.ep_id
		place_code    = order.place_code
		booth_number  = order.booth_number
		order_date    = order.order_date
		batch_name    = order.batch_name
		note          = order.note

		ws.write(current_row, 1, "DocNumber: ", xf_bold)
		ws.write_merge(current_row, current_row, 2, 3, label=doc_number)		
		current_row += 1
		write_header(ws, current_row, 'order', xf_italic)
		current_row += 1
		ws.write(current_row, 1, place_code)
		ws.write(current_row, 2, booth_number)
		ws.write(current_row, 3, order_date)
		ws.write(current_row, 4, batch_name)
		ws.write(current_row, 5, note)
		current_row += 1
		
      # [
      #   "TB-SK-30-2X6-RE",
      #   1.0,
      #   90.0,
      #   true,
      #   ""
      # ],

		# items
		ws.write(current_row, 1, "Line Items", xf_bold)
		current_row += 1
		write_header(ws, current_row, 'line_items', xf_italic)
		current_row += 1
		for item in order.items.all():
			
			# ws.write(current_row, 1, str(item.item_number))
			ws.write(current_row, 1, str(item.ep_id))
			ws.write(current_row, 2, str(item.qty))
			ws.write(current_row, 3, str(item.unit_price))
			ws.write(current_row, 4, str(item.taxable))
			ws.write(current_row, 5, str(item.notes))

			# for i, derp in enumerate(item):
			# 	ws.write(current_row, i+1, str(derp))
			current_row += 1
		
		ws.write(current_row, 1, "Payments", xf_bold)
		current_row += 1	
		write_header(ws, current_row, 'payments', xf_italic)
		current_row += 1
		# payments
		for payment in order.payments.all():
			payment_date       = payment.payment_date
			authorization_code = payment.authorization_code
			expiration_date    = payment.expiration_date
			credit_card_number = payment.credit_card_number
			payment_amount     = payment.payment_amount
			payment_type       = payment.payment_type
			credit_card_id     = payment.credit_card_id
			check_number       = payment.check_number

			ws.write(current_row, 1,payment_date)
			ws.write(current_row, 2,authorization_code)
			ws.write(current_row, 3,expiration_date)
			ws.write(current_row, 4,credit_card_number)
			ws.write(current_row, 5,payment_amount)
			ws.write(current_row, 6,payment_type)
			ws.write(current_row, 7,credit_card_id)
			ws.write(current_row, 8,check_number)				
			ws.write(current_row, 9, "gs-id: %s" % payment.gs_id)
			current_row += 1

		current_row += 2	
	
	workbook_dir_path = os.path.abspath('./reports')
	workbook_path     = os.path.join(workbook_dir_path, filename)
	
	if not os.path.exists(workbook_dir_path):
		os.makedirs(workbook_dir_path)
	
	workbook.save( workbook_path )

	return workbook_path

