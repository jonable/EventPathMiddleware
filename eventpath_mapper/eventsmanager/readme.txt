Incase eventdata is wiped.
Export a csv of events from DBSYS.exe
and use the following code to import events

from entries.models import Order
from eventsmanager.utils import update_events

events = dbsys_events('/Volumes/testing/events_data.TXT')
update_events(events)