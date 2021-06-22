import xlwt, xlrd

from itempricelist.models import ItemRate, PriceLevel

def bar():
	import csv
	csv_file = open('../invitem.TXT', 'r')
	derp = csv_file.readlines()
	data = []
	for i, row in enumerate(csv.reader(derp)):
		new_row = []
		for cell in row:
			new_row.append(cell)
		
		data.append(', '.join(["%s" % x for x in new_row]))

		fi = open('../derp.csv', 'w')
		fi.write('\r\n'.join(data))
		fi.close()


def foo(path_to):
	workbook = xlrd.open_workbook('../matrix-compiled.xls')
	sheet = workbook.sheet_by_index(0)
	
	for x in range(1, sheet.nrows):
		# _row = sheet.row(x)
		derp = None
		price_lvl_name = sheet.cell(x, 1).value
		price_lvl = PriceLevel.objects.get(name=price_lvl_name)
		
		adv_price = 0.00
		std_price = 0.00
		if sheet.cell(x,2).ctype == 2:
			adv_price = sheet.cell(x,2).value

		if sheet.cell(x,3).ctype == 2:
			std_price = sheet.cell(x,3).value
		try:
			derp, created = ItemRate.objects.get_or_create(
				name=sheet.cell(x, 0).value, 
				adv_price=adv_price, 
				std_price=std_price, 
				price_lvl=price_lvl)			
		except Exception, e:
			print x
			continue
		derp.save()


def parse_price_level_matrx(path_to_workbook):
	plm = xlrd.open_workbook(path_to_workbook)
	sheet = plm.sheet_by_index(0)
	# find the start of the price levels
	price_levels = []
	price_levels_row = 0
	for i in range(sheet.nrows):
		price_levels = [(j, x.value) for j, x in enumerate(sheet.row(i)) if 'Price Level' in x.value]
		if price_levels:
			price_levels_row = i
			break

	derp = []
	for i in range(price_levels_row + 2, sheet.nrows):
		name = sheet.cell(i, 0).value
		for col, lvl in price_levels:
			from_lvl = 0.0
			adv      = 0.0
			reg      = 0.0
			increase = 0.0
			
			if '118' in lvl:
				adv      = sheet.cell(i, col).value
				reg      = sheet.cell(i, col + 1).value
				increase = sheet.cell(i, col + 2).value
			else:
				from_lvl = sheet.cell(i, col).value
				adv      = sheet.cell(i, col + 1).value
				reg      = sheet.cell(i, col + 2).value
				increase = sheet.cell(i, col + 3).value


			derp.append(dict(name=name, lvl=lvl, from_lvl=from_lvl, adv=adv, reg=reg, increase=increase))

	compiled_list = xlwt.Workbook()
	new_sheet = compiled_list.add_sheet('Price List')

	new_sheet.write(0, 0, label='ItemName')
	new_sheet.write(0, 1, label='PriceLevel')
	new_sheet.write(0, 2, label='Advance')
	new_sheet.write(0, 3, label='Regular')
	new_sheet.write(0, 4, label='From118')
	new_sheet.write(0, 5, label='Increase')

	for row, data in enumerate(derp):
		
		new_sheet.write(row + 1, 0, label=data['name'])
		new_sheet.write(row + 1, 1, label=data['lvl'])
		new_sheet.write(row + 1, 2, label=data['adv'])
		new_sheet.write(row + 1, 3, label=data['reg'])
		new_sheet.write(row + 1, 4, label=data['from_lvl'])
		new_sheet.write(row + 1, 5, label=data['increase'])













