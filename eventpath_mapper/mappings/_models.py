from django.db import models
# attempt to normalze the module entry table
# i feel like this could create a mess and i'm implemnating it wrong.
# 
# Probably won't be an issue at the time but could later on


class BaseAudits(object):
	created  = models.DateTimeField('', auto_now=False, auto_now_add=True)
	modified = models.DateTimeField('', auto_now=True, auto_now_add=False)


class ModuleEntry(models.Model):

	CREATE = 'cr'
	READ   = 'rd'
	UPDATE = 'ud'
	DELETE = 'dl'

	ACTION_TYPES = (
		(CREATE, 'Created'),
		(READ, 'Read'),
		(UPDATE, 'Updated'),
		(DELETE, 'Deleted'),
	)		

	module = models.ForeignKey('AppModule', related_name="entries")

	action = models.CharField(max_length=3, choices=ACTION_TYPES, default=CREATE)

class ModuleEntryId(models.Model, BaseAudits):


	name        = models.CharField('ID', max_length=255)
	application = models.ForeignKey('Application', related_name="module_ids")
	moduleentry = models.ForeignKey('ModuleEntry', related_name="module_ids")





































class MapItemType(models.Model):

	name = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name

class MapItem(models.Model, BaseAudits):

	name        = models.CharField(max_length=255)
	item        = models.CharField('GoShow Item Id', max_length=255)
	application = models.ForeignKey('Application', related_name='item')
	item_type   = models.ForeignKey('MapItemType')

	def __unicode__(self):
		return self.name




