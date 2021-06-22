from django.conf.urls import url
from django.contrib import admin

from entries2.entry_report import excel_report2
from .models import Entry, Event, Order, OrderItem, OrderPayment, CustomerAddress
# Register your models here.



class OrderInline(admin.TabularInline):
	model = Order

class OrderItemInline(admin.TabularInline):
	model = OrderItem

class OrderPaymentInline(admin.TabularInline):
	model = OrderPayment

class CustomerAddressInline(admin.TabularInline):
	model = CustomerAddress


from django.http import HttpResponse
import os
def entry_report_link(obj):
	return "<a href=\"report/%s\">Report</a>" % (obj.pk)
	# if obj.success:
	# 	return "<a href=\"report/%s\">Report</a>" % (obj.pk)
	# return "Report"

entry_report_link.short_description = 'Entry Report'
entry_report_link.allow_tags = True
class EntryAdmin(admin.ModelAdmin):
	'''
		Admin View for Entry
	'''
	# inlines = (OrderInline,)
	list_display = ('created', 'success', entry_report_link)
	
	def get_urls(self):
		urls = super(EntryAdmin, self).get_urls()
		my_urls = [
			url(r'^report/(?P<pk>\d+)/$', self.entry_report)
		]
		return my_urls + urls



	def entry_report(self, request, pk):
		entry = Entry.objects.get(pk=pk)
		workbook_path = excel_report2(entry)


		path = workbook_path
		if os.path.exists(path):
			with open(path, "rb") as excel:
				data = excel.read()

		response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(workbook_path)
		return response

		# response = HttpResponse(content_type='application/vnd.ms-excel')
		# response['Content-Disposition'] = 'attachment; filename=%s' % (os.path.basename(workbook_path))
		# response['Content-Length'] = os.path.getsize(workbook_path)
		# response.write(open(workbook_path, 'r').read())
		# return response

admin.site.register(Entry, EntryAdmin)

class EventAdmin(admin.ModelAdmin): pass
admin.site.register(Event, EventAdmin)

class OrderAdmin(admin.ModelAdmin):
	'''
		Admin View for Order
	'''
	inlines = (OrderItemInline, OrderPaymentInline,CustomerAddressInline,)

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
	'''
		Admin View for OrderItem
	'''
	pass

admin.site.register(OrderItem, OrderItemAdmin)

class OrderPaymentAdmin(admin.ModelAdmin):
	'''
		Admin View for OrderPayment
	'''
	pass

admin.site.register(OrderPayment, OrderPaymentAdmin)

class CustomerAddressAdmin(admin.ModelAdmin):
	'''
		Admin View for CustomerAddress
	'''
	pass

admin.site.register(CustomerAddress, CustomerAddressAdmin)