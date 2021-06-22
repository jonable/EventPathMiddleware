import json 

from django.template import Context, Template

from .models import MapItem, MapItemOption, MapItemOptionValue

MAP_EP_TO_GS = 1
MAP_GS_TO_EP = 2



class MapItemNotFoundException(Exception): pass


def epitem_exists(item_number):
	# check if an ep item exist
	# if it does not exist
	# does the code map to another item?
	# For instance DY-AD-SH-ST-OT too DY-AD
	invitems = json.load(open('../data/invitemnames.json', 'r'))
	return item_number in invitems


# def get_format_optionvalues(mapitemoption, value):
# 	mapitemoptionvalue = mapitemoption.values.get(name=value)
# 	if mapitemoptionvalue:
# 		return mapitemoptionvalue.ep_abbrv

def get_format_options(options):	
	result = {}
	# smells
	for option in options:
		mapitemoption = MapItemOption.objects.filter(gs_name=option[0]).first()
		if mapitemoption:
			mapitemoptionvalue = mapitemoption.values.get(name=option[1])
			# mapitemoptionvalue = MapItemOptionValue.objects.filter(name=option[1]).first()
			if mapitemoptionvalue:
				result[mapitemoption.ep_name] = mapitemoptionvalue.ep_abbrv
	return result

def render_template(template, context):
	t = Template(template)
	c = Context(context)
	return t.render(c).strip()

# need to inform user if item is not found...
def map_item(item_id, options=None):
	result = ''
	# ...
	try:
		mapped_item = MapItem.objects.get(gs_item=item_id)
	except MapItem.DoesNotExist:
		raise MapItemNotFoundException('No EventPath item found for: %s' % item_id)

	result = mapped_item.ep_item
	if mapped_item.template and options:
		option_format_map = get_format_options(options)
		
		if option_format_map:
			# need to sort option_format_map
			# and then dump it into mapped_item.template.format(option_format_map)
			result = render_template(mapped_item.template, option_format_map)

	# this fails because a bunch of items haven't made it inot eventpath first
	# How about, if item is not being pieced together.. just return the item number?
	# This will cause errors...
	# Use a back up item number? 
	# For instance: 
	# DY-AD-SH-ST-OT could map too DY-AD...
			if epitem_exists(result):
				return result
			else:
				import ipdb; ipdb.set_trace()
				raise MapItemNotFoundException('No matching EventPath item number for: %s' % result)


	return result
	
def test_mappings(entry):
	for o in entry.orders.all():
		print o.place_code, o.description   
		for item in o.items.all():
			item_number = map_item(item.item_name, item.options)        
			if not item_number:				
				print "Item Not Found: %s" % item.item_name
			else:
				print item_number
				item.item_number = item_number
				item.save()
		print ''

# def update_item_options(gs_options):
# 	# create new item, else skip.
# 	for x in options:
# 		obj, created = MapItemOption.objects.get_or_create(gs_item= x.get('item_name'))
# 		if created:
# 			x.get('item_name') for x in options:
# 			obj.ep_name = ''
# 			obj.order = 0
# 			obj.save()
# 			continue