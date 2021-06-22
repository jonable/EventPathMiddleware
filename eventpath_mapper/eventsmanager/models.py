from django.db import models
from jsonfield import JSONField

# Create your models here.

class EventData(models.Model):
	"""Copy of EventPath Event Data"""
	event_code    = models.CharField(max_length=255)
	event_subcode = models.CharField(max_length=255)
	description   = models.CharField(max_length=255, blank=True)
	startdate     = models.CharField(max_length=255)
	batch_name    = models.CharField(max_length=255, blank=True)
	data          = JSONField('Update Data')

	def __str__(self):
		return "%s - %s" % (self.event_code, self.event_subcode)


	class Meta:
		unique_together = ('event_code', 'event_subcode',)
		index_together = ('event_code', 'event_subcode',)
		verbose_name= 'Events'
		verbose_name_plural = 'Events'
