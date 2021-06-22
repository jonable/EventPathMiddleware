from django.contrib import admin
from django.db import models


from itempricelist	.models import (
	PriceLevel, DrayageRate, LaborRate, 
	ItemRate, PriceList
)

class ItemRateAdminInline(admin.TabularInline):
    model = ItemRate    
    fields = ('name', 'category', 'adv_price', 'std_price')

class PriceLevelAdmin(admin.ModelAdmin):
	inlines = (ItemRateAdminInline, )
admin.site.register(PriceLevel, PriceLevelAdmin)

class DrayageRateAdmin(admin.ModelAdmin): pass
admin.site.register(DrayageRate, DrayageRateAdmin)

class LaborRateAdmin(admin.ModelAdmin): pass
admin.site.register(LaborRate, LaborRateAdmin)

class ItemRateAdmin(admin.ModelAdmin): pass
admin.site.register(ItemRate, ItemRateAdmin)

class PriceListAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': admin.widgets.FilteredSelectMultiple("Options", False, attrs={'rows':'2'})},
    }
admin.site.register(PriceList, PriceListAdmin)
