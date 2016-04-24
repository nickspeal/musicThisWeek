#!/usr/bin/python
'''Get upcoming shows from bandsintown and create a spotify playlist'''

import requests
import json


class Event(object):
	def __init__(self, event_dict):
		self.title = event_dict['title']
		self.url = event_dict['url']
		self.description = event_dict['description']
		self.id = event_dict['id']
		self.venue_name = event_dict['venue_name']
		self.performers = event_dict['performers']
		self.all_day = event_dict['all_day']
		
		self.artist = None # TODO parse title creatively

	def __repr__(self):
		return "Title: %r \nVenue: %r \n" % (self.title, self.venue_name)

class EventBuilder(object):
	def __init__(self, json_response):
		self.json_response = json_response

	def build(self):
		events = self.json_response['events']['event']
		for event_dict in events:
			yield Event(event_dict)

class SearchArgs(object):
	def __init__(self, location = 'San+Francisco', time='This+Weekend', nResults=100):
		self.location = location
		self.time = time
		self.nResults = nResults

class EventFinder(object):
	def __init__(self, searchArgs):
			self.searchArgs = searchArgs
			
			eventfulEndpoint = self.assembleEndpoint()
			
			# Hit the server and generate list of upcoming events
			self.resp = requests.get(eventfulEndpoint)
			if (self.resp.status_code != 200):
				raise UnexpectedStatusCode("Bad response from server. Status code: %i" %self.resp.status_code)
			if not self.resp.ok:
				raise BadResponse("Server Response Not OK")
			
			builder = EventBuilder(self.resp.json())
			
			self.upcomingEvents = []
			for event in builder.build():
				self.upcomingEvents.append(event)
			


	def assembleEndpoint(self):
		'''Receives search parameters and returns a URL for the endpoint'''
		# TODO specify provider as an argument, and call this method for each provider (maybe)
		
		# EVENTFUL
		EVENTFUL_KEY = 'xmwwM432wt4KZF5c'	
		baseURL = 'http://api.eventful.com/json/events/search?app_key=%s' % EVENTFUL_KEY
		filters = ['category=music||concerts', #seems to return the same results for music or concerts, so this might be unnecessary
							 'location=%s' %self.searchArgs.location,
							 'time=%s' %self.searchArgs.time,
							 'page_size=%s' %self.searchArgs.nResults]
			
		URL = baseURL	
		for f in filters:
			URL += '&' + f
		# print 'Hitting Endpoint : ' + URL

		return URL

	def filterForKnownVenues(self):
		'''Reduces the upcomingEvents list down to just a list of events at known venues. An attempt to filter for concerts'''

		validVenues = ['Fillmore', 'Kilowatt', 'The Greek Theatre', 'Amnesia', "Thee Parkside", "Parkside", "The Chapel", "The Independent", "Doc's Lab", "Public Works", "MAIN STREETS MARKET AND CAFE", "Ashkenaz", "Freight & Salvage", "Fireside Lounge", "The Huddle", "Brick & Mortar", "Milk Bar", "Biscuits and Blues"]
		self.filteredUpcomingEvents = []
		for event in self.upcomingEvents:
			for venue in validVenues:
				if venue in event.venue_name:
					if event not in self.filteredUpcomingEvents:
						self.filteredUpcomingEvents.append(event)
		print "Filtered events. %i of %i events are at one of the valid venues" % (len(self.filteredUpcomingEvents), len(self.upcomingEvents))

	def saveEventsToFile(self, filename):
		with open(filename, 'w') as outfile:
			json.dump(self.resp.json(), outfile)

if __name__ == '__main__':
	searchArgs = SearchArgs(location = 'San+Francisco', time = 'Next+14+days', nResults = 15)
	filename = "./tmp/events.json"
	EF = EventFinder(searchArgs)
	EF.saveEventsToFile(filename)

	#print "Success. Saved %i events matching the search query" %len(EF.upcomingEvents)
	#EF.filterForKnownVenues()
	
	# for event in EF.upcomingEvents:
	# 	print event
	# # # Other filters
			# 'location=94110&within=30&units=miles'
			# 'time=This+Weekend'



# TODO items

# Clean up search argument specification:
	# import urllib
	# urllib.encode(searchArgs)