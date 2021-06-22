from django.contrib import admin

from mappings.models import (
	AppModule, Application, MapModuleId, 
	MapItem, MapItemOption, MapItemOptionValue
)

class ApplicationInline(admin.TabularInline):
	model = Application

class AppModuleInline(admin.TabularInline):
	model = AppModule    

# class MapItemTypeInline(admin.TabularInline):
# 	model = MapItemType    
class MapItemOptionInline(admin.TabularInline):
	model = MapItemOption.items.through

class MapItemOptionValueInline(admin.TabularInline):
	# model = MapItemOptionValue
	model = MapItemOptionValue

class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')

admin.site.register(Application, ApplicationAdmin)

class AppModuleAdmin(admin.ModelAdmin):  pass
admin.site.register(AppModule, AppModuleAdmin)


class MapModuleIdAdmin(admin.ModelAdmin):
	# inlines = [AppModuleInline, AppModuleInline]
	list_display = ('name', 'application', 'module', 'is_prime')

admin.site.register(MapModuleId, MapModuleIdAdmin)

# class MapItemTypeAdmin(admin.ModelAdmin): pass
# admin.site.register(MapItemType, MapItemTypeAdmin)

class MapItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'gs_item', 'ep_item', 'template')
	list_editable = ('name', 'gs_item', 'ep_item', 'template')
	search_fields = ('name', 'ep_item', 'gs_item')
	inlines = (MapItemOptionInline,)

	def get_queryset(self, request):
		qs = super(MapItemAdmin, self).get_queryset(request)
		return qs.filter(active=True)

admin.site.register(MapItem, MapItemAdmin)

class MapItemOptionAdmin(admin.ModelAdmin):
	list_display = ('gs_name', 'ep_name')
	inlines = (MapItemOptionValueInline,)

admin.site.register(MapItemOption, MapItemOptionAdmin)

