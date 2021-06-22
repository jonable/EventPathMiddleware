from django.core.urlresolvers import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect

from django.conf.urls import url

# Register your models here.
from .models import EventData
from django.core.urlresolvers import reverse

def upload_data_to_show(modeladmin, request, queryset):
	event = queryset[0]
	request.session['event_subcode'] = event.event_subcode
	request.session['event_code'] = event.event_code
	return HttpResponseRedirect(reverse('upload_gs_json'))

upload_data_to_show.short_description = "Select a show to upload data to"


def upload_data_to_show_link(obj):
	return "<a href=\"upload_data_link?event_code=%s&event_subcode=%s\">upload</a>" % (obj.event_code, obj.event_subcode)
upload_data_to_show_link.short_description = 'Upload Data'
upload_data_to_show_link.allow_tags = True


class EventDataAdmin(admin.ModelAdmin):
	search_fields = ['description', 'event_code']
	actions = [upload_data_to_show]
	list_display = ('event_code', 'event_subcode', upload_data_to_show_link,)


	def get_urls(self):

		urls = super(EventDataAdmin, self).get_urls()
		my_urls = [
			url(r'^upload_data_link/$', self.upload_data_view),
		]
		return my_urls + urls

	def upload_data_view(self, request):
		# context = dict(
		#    # Include common variables for rendering the admin template.
		#    self.admin_site.each_context(request),
		#    # Anything else you want in the context...
		#    key=value,
		# )

		request.session['event_code'] = request.GET.get('event_code')
		request.session['event_subcode'] = request.GET.get('event_subcode')
		return HttpResponseRedirect(reverse('upload_gs_json'))


admin.site.register(EventData, EventDataAdmin)
