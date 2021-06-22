from django.db import models

# These models are to map the difference between the two (multiple?) applications.

# Import note from the docs:
# https://docs.djangoproject.com/en/1.8/topics/migrations/#postgresql
# PostgreSQL is the most capable of all the databases here in terms of schema support; the only caveat is that adding columns 
# with default values will cause a full rewrite of the table, for a time proportional to its size.
# For this reason, it's recommended you always create new columns with null=True, as this way they will be added immediately.


# mixin doesn't work
class AuditsMixin(object):
	created  = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified = models.DateTimeField('', auto_now=True, auto_now_add=False)


class AppModule(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name

class Application(models.Model):
	name        = models.CharField(max_length=255)
	code        = models.CharField('Application Code', max_length=5)
	description = models.TextField(blank=True)

	def __unicode__(self):
		return self.name

class MapModuleId(models.Model):
	# store the ID field names for each applications module
	# application	module	key	        is_prime
	# ep	        orders	DocNumber	TRUE

	# Could be mushed into MapItem?
	name        = models.CharField('ID Field Name', max_length=255)
	application = models.ForeignKey('Application')
	module      = models.ForeignKey('AppModule')	
	is_prime    = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name




# class MapItemTypeManager(models.Manager):
#     def get_by_natural_key(self, name):
#         return self.get(name=name)

# class MapItemType(models.Model):

# 	name = models.CharField(max_length=255)
# 	objects = MapItemTypeManager()

# 	def natural_key(self):
# 		return [self.name]

# 	def __unicode__(self):
# 		return self.name

class MapItem(models.Model, AuditsMixin):
	# generic table to map items like product id's, date formats, ...
	# like entries.ModuleEntry this table wants to scale horizontally
	# how to abstract 
	name      = models.CharField('EP Name', max_length=255)
	
	# template  = models.CharField('EPCode Template', max_length=255, blank=True)
	template  = models.TextField('EPCode Template', blank=True)

	gs_name   = models.CharField('GS Name', max_length=255, default='')
	# pricelist = models.CharField('Pricelist', max_length=255)
	
	gs_item   = models.CharField('GoShow Item Id', max_length=255)
	ep_item   = models.CharField('EventPath Item Id', max_length=255)
	# item_type = models.ForeignKey('MapItemType')
	active    = models.BooleanField(default=True)
	
	created   = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified  = models.DateTimeField('', auto_now=True, auto_now_add=False)

	def __unicode__(self):
		return self.name

# def add_mapped_item(item):	
# 	results = None
# 	errors = None
# 	name = item.get('epname') or item.get('gsid') or ''
# 	template = ''
# 	gs_name = item.get('gsid') or ''
# 	gs_item = item.get('gsid') or ''
# 	ep_item = item.get('epid') or ''

# 	mapitem = MapItem()
# 	mapitem.name = name
# 	mapitem.template = template
# 	mapitem.gs_name = gs_name
# 	mapitem.gs_item = gs_item
# 	mapitem.ep_item = ep_item
	
# 	try:
# 		mapitem.save()
# 		results = mapitem
# 	except Exception, e:
# 		print e
# 		errors = item

# 	return results, errors


# item_type = MapItemType.objects.get(pk=1)
# for x in newitems:
# 	template  = ''
# 	name      = x
# 	gs_name   = x
# 	pricelist = '118'
# 	ep_item   = ''
# 	gs_item   = ''
# 	for y in pl118:
# 		if y[0] == x:
# 			gs_item = y[1]
# 			break
# 	_obj = MapItem.objects.create(template=template, name=name, gs_name=gs_name, pricelist=pricelist, ep_item=ep_item, gs_item=gs_item, item_type=item_type)



class MapItemOption(models.Model):
	gs_name  = models.CharField('Option Name', max_length=255, blank=True)
	ep_name  = models.CharField('EP Option Name', max_length=255, blank=True)
	items    = models.ManyToManyField(MapItem, related_name="item_options", blank=True)	
	# template = models.CharField('EPCode Template', max_length=255, blank=True)
	order    = models.IntegerField('Abbrv Order In EPCode')

	def __unicode__(self):
		return self.gs_name

class MapItemOptionValue(models.Model):

	name     = models.CharField('Value', max_length=255)
	ep_abbrv = models.CharField('EP Code Abbrv', max_length=64)
	order    = models.IntegerField('Abbrv Order In EPCode', default=0)
	option   = models.ForeignKey(MapItemOption, related_name="values")


	def __unicode__(self):
		return self.name

