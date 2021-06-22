from django.db import models
	
	# Create your models here.

class PriceLevel(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name


class DrayageRate(models.Model):
	name      = models.CharField(max_length=255)
	state     = models.CharField(max_length=255, blank=True)
	facility  = models.CharField(max_length=255, blank=True)
	adv_price = models.DecimalField(max_digits=11, decimal_places=2)
	std_price = models.DecimalField(max_digits=11, decimal_places=2)
	price_lvl = models.ForeignKey('PriceLevel')

	def __unicode__(self):
		return self.name

	
class LaborRate(models.Model):
	name      = models.CharField(max_length=255)
	category  = models.CharField(choices=[
		('general', 'general'),
		('booth', 'booth'),
		('cleaning', 'cleaning'),
		('forklift', 'forklift'),
		('porter', 'porter')], max_length=255, blank=True)	
	state     = models.CharField(max_length=255, blank=True)
	facility  = models.CharField(max_length=255, blank=True)
	straight  = models.DecimalField(max_digits=11, decimal_places=2)
	over      = models.DecimalField(max_digits=11, decimal_places=2)
	double    = models.DecimalField(max_digits=11, decimal_places=2)
	price_lvl = models.ForeignKey('PriceLevel', blank=True, null=True)

	def __unicode__(self):
		return self.name


class ItemRate(models.Model):
	name         = models.CharField(max_length=255)
	description  = models.TextField(blank=True)
	category     = models.CharField(max_length=255, blank=True)
	sub_category = models.CharField(max_length=255, blank=True)
	adv_price    = models.DecimalField(max_digits=11, decimal_places=2)
	std_price    = models.DecimalField(max_digits=11, decimal_places=2)
	price_lvl    = models.ForeignKey('PriceLevel')

	def __unicode__(self):
		return self.name

class PriceList(models.Model):
	name        = models.CharField(max_length=255)
	price_level = models.ForeignKey('PriceLevel')
	drayage     = models.ForeignKey('DrayageRate')
	LaborRate   = models.ManyToManyField('LaborRate')

	def __unicode__(self):
		return self.name


