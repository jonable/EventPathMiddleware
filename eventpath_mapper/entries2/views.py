import time, os
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.contrib import messages

from entries2.utils import update_order, import_to_eventpath

class UploadFileForm(forms.Form):
	file = forms.FileField()
	event_code = forms.CharField(widget=forms.HiddenInput())
	event_subcode = forms.CharField(widget=forms.HiddenInput())

def upload_gs_json(request):
	context       = {}
	event_code    = request.session.get('event_code')
	event_subcode = request.session.get('event_subcode')
	
	if not event_code and not event_subcode:
		messages.add_message(request, messages.WARNING, 'An Event Must Be Selected First')
		return HttpResponseRedirect(reverse('admin:eventsmanager_eventdata_changelist'))	

	context['form'] = UploadFileForm(initial={
		'event_code': event_code, 
		'event_subcode': event_subcode
	})
	context['event_code']    = event_code
	context['event_subcode'] = event_subcode
	return render(request, 'entries2/upload.html', context)


def handle_uploaded_file(f, event_code):
	file_path = os.path.abspath('../data/eventorders/%s' % event_code)
	file_name = str(int(time.time()))
	complete_path = os.path.join(file_path, "%s.json" % file_name)
	if not os.path.exists(file_path):
		os.makedirs(file_path)
	with open(complete_path, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	# event_orders = json.load(open(complete_path, 'r'))
	# parse_event_orders(event_orders)
	return complete_path

def upload_action(request):		
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			path_to_upload = handle_uploaded_file(request.FILES['file'], form.data['event_code'])
			# request.session['event_code']        = ''
			# request.session['event_subcode']     = ''
			# request.session['event_orders_json'] = path_to_upload
			# 
			event_code    = request.session.get('event_code')
			event_subcode = request.session.get('event_subcode')			
			
			results, entry = update_order(event_code, event_subcode, path_to_upload)
			# try:
			# 	update_order(event_code, event_subcode, path_to_upload)
			# except Exception:
			# 	messages.error(request, 'Error Loading Data for %s - %s' % (event_code, event_subcode))
			# 	return HttpResponseRedirect(reverse('admin:eventsmanager_eventdata_changelist'))
			
			try:
				import_to_eventpath(entry)
			except Exception, e:
				raise e

			messages.success(request, mark_safe('Event Orders uploaded to EventPath - <a href="/admin/entries2/entry/report/%s">click to download report</a>' % entry.pk)) 
			return HttpResponseRedirect(reverse('admin:eventsmanager_eventdata_changelist'))

		# messages.add_message(request, messages.WARNING, 'An Event Must Be Selected First')
	return HttpResponseRedirect(reverse('upload_gs_json'))



# def update_order(request):
# 	pass





















		
# user selects the event from teh database
# uploads the goshow json file 
# file is parsed grouping all orders by customer

# set the event

# for creating an order
# store all the orderitems and payments
# run create_order
# set all the inputed items/payments in_ep to True

# for updating an order
# get the order_number for the customer and set the event
# check the middleware db for existing payments and ordered items
# of payment or orderitem in_ep == False
# set the ordernumber
# dump items and payments into the order











