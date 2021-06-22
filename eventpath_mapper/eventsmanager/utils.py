import csv
import json
from collections import OrderedDict
from .models import EventData

def events_fieldnames():
	return [
		'EventCode',
		'EventSubCode',
		'EventType',
		'SubContracted',
		'Locale',
		'Description',
		'ShortDescription',
		'EventGroup',
		'EventStatus',
		'SalespersonCode',
		'SupervisorCode',
		'EventPlaceCode',
		'EventPlaceAddressCode',
		'EventMgmntPlaceCode',
		'EventMgmntAddressCode',
		'EventAssociationCode',
		'RFPDate',
		'SoldDate',
		'SalesTaxCode',
		'PaymentTerms',
		'PriceLevel',
		'DiscountCutoffDate',
		'SendAssociationKitsDate',
		'SendAssociationKitsTime',
		'SendExhibitorKitsDate',
		'SendExhibitorKitsTime',
		'CompanySetupStartDate',
		'CompanySetupStartTime',
		'CompanySetupEndDate',
		'CompanySetupEndTime',
		'ExhibitorSetupStartDate',
		'ExhibitorSetupStartTime',
		'ExhibitorSetupEndDate',
		'ExhibitorSetupEndTime',
		'EventStartDate',
		'EventSDate',
		'EventStartTime',
		'EventEndDate',
		'EventEndTime',
		'ExhibitorBDownStartDate',
		'ExhibitorBDownStartTime',
		'ExhibitorBDownEndDate',
		'ExhibitorBDownEndTime',
		'CompanyBDownStartDate',
		'CompanyBDownStartTime',
		'CompanyBDownEndDate',
		'CompanyBDownEndTime',
		'MgmntServiceSpecKits',
		'MgmntFloorPlan',
		'RegistrationCountersQty',
		'RegistrationFurniture',
		'RegAddtlCountersCharge',
		'RegistrationOtherItems',
		'FurnitureEventOffice',
		'FurnitureEventBooth',
		'FurnitureEventLounges',
		'DiscountsFurniturePercent',
		'DiscountSignsPercent',
		'DiscountsOtherPercent',
		'DrayageNoChargeLbs',
		'DrayageAdditionalRate',
		'AisleCarpet',
		'AisleCarpetCharge',
		'AisleCarpetChargePer',
		'AisleCarpetColor',
		'AisleCarpetCleaning',
		'AisleCarpetCleaningCharge',
		'AisleCarpetCleaningChgPer',
		'MaskingNoChargeFeet',
		'Masking3Charge',
		'Masking8Charge',
		'MaskingOtherDesc1',
		'MaskingOtherCharge1',
		'MaskingOtherDesc2',
		'MaskingOtherCharge2',
		'EntranceWay',
		'EntranceWayCharge',
		'AisleSign',
		'AisleSignCharge',
		'ElectricalServiceProvider',
		'Electrical3rdPartyProv',
		'ElectricalBlanket',
		'ElectricalExhibitorOrders',
		'KitsCompanyMail',
		'KitsManagementMail',
		'KitsQuantity',
		'KitsStapled',
		'KitsLetter',
		'KitsCollated',
		'KitsFullKit',
		'KitsMgmntApprovalSentDate',
		'BoothCharge',
		'BoothChargeDescription',
		'BoothColor',
		'BoothQty',
		'BoothSize',
		'Booth8ftBackwall',
		'Booth3ftSidewall',
		'BoothBareTable',
		'BoothDrapedTable',
		'BoothTableSize',
		'BoothFoldingChairQty',
		'BoothWasteBasket',
		'BoothSign',
		'BoothNumber',
		'BoothLogo',
		'BoothExtras',
		'LaborDrayage',
		'SpecialDecorating',
		'SLSBankAccount',
		'SLSARAccount',
		'SLSSalesAccount',
		'SLSReturnsAccount',
		'SLSCOGSAccount',
		'SLSWriteoffsAccount',
		'SLSFinChargeAccount',
		'SLSTermsDiscAccount',
		'CreatedUserID',
		'CreatedDate',
		'CreatedTime',
		'ModifiedUserID',
		'ModifiedDate',
		'ModifiedTime',
		'Note',
		]

def remove_bad_ascii(text):
	""" 
	Remove ascii characters that are throwing UnicodeDecodeError
	It could be fancier, but again lazy
	:text <string> ascii text i suppose
	:results <string>
	"""
	results = ''

	for i, x in enumerate(text):
		try:
			results += x.encode()			
		except UnicodeDecodeError:
			continue

	return results

def dbsys_events(filename):
	text = open(filename, 'r').read()
	open(filename, 'w').write(remove_bad_ascii(text))
	return csv_to_dict(filename)

def csv_to_dict(filename):
	"""
	THIS IS SPECIFIC TO Events csv created with DBSYS.exe, the dbisam utility
	It assumes 124 fields, anything greater than 124 is pieces of the notes field
	csv chopped up because of a comma within the text... confusing
	Convert a csv file with fieldnames as the header to a dictionary wrapped in a list
	:filename <string> path to the csv file
	:returns <list>
	"""
	results = []

	with open(filename, 'rb') as _csvfile:
# _csvfile = open(filename, 'rb')
		dialect = csv.Sniffer().sniff(_csvfile.read(1024))
		_csvfile.seek(0)		
		spamreader = csv.reader(_csvfile, dialect)

		# field_names = spamreader.next()
		field_names = events_fieldnames()

		for row in spamreader:							
			tmp = OrderedDict()
			# notes field fudges up csv
			# not the best solution but 
			try:
				if len(row) <= 124:
					row[123] = ''.join(row[123:])
			except Exception, e:
				print row[:1]


			for i, value in enumerate(row[:124]):
				_field = field_names[i]
				tmp[_field] = value
			results.append(tmp)

	return results

def update_events(events):
	for event in events:		
		_obj, created = EventData.objects.get_or_create(
			event_code=event['EventCode'], 
			event_subcode=event['EventSubCode']
		)
		_obj.description = event['Description']
		if created:
			_obj.data = json.dumps(event)
		_obj.save()
