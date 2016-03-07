#!/usr/bin/python
'''Get upcoming shows from bandsintown and create a spotify playlist'''

import requests


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
			resp = requests.get(eventfulEndpoint)
			if (resp.status_code != 200):
				raise UnexpectedStatusCode("Bad response from server. Status code: %i" %resp.status_code)
			if not resp.ok:
				raise BadResponse("Server Response Not OK")
			
			builder = EventBuilder(resp.json())
			
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
		print 'Hitting Endpoint : ' + URL

		return URL

	

if __name__ == '__main__':
	searchArgs = SearchArgs(location = 'San+Francisco', time = 'Next+14+days', nResults = 10)
	EF = EventFinder(searchArgs)
	print "Success. Saved %i events matching the search query" %len(EF.upcomingEvents)
	# for event in EF.upcomingEvents:
	# 	print event
	# # Other filters
			# 'location=94110&within=30&units=miles'
			# 'time=This+Weekend'