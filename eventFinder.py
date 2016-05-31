#!/usr/bin/python
''' Crawl the web for upcoming concerts and return a list of artists'''

import requests
import json


class EventFinder(object):
	def __init__(self, searchArgs):
		self.searchArgs = searchArgs
		self.upcomingEvents = [] #A list of Event objects
		self.validVenues = ['The Fillmore', 'Kilowatt', 'The Greek Theatre', 'Amnesia', "Thee Parkside", "Parkside", "The Chapel", "The Independent", "Doc's Lab", "MAIN STREETS MARKET AND CAFE", "Ashkenaz", "Freight & Salvage", "Fireside Lounge", "The Huddle", "Brick & Mortar", "Milk Bar", "Biscuits and Blues"]

		#TODO break down large nResults into requested number of pages. Or specify max elapsed time?
		# for venue in self.validVenues:
		for page_number in range(1,10):
			searchArgs['page_number'] = page_number
			self.findEvents(searchArgs)
			

			print "Success. Saved %i events matching the search query" %len(self.upcomingEvents)
		for event in self.upcomingEvents:
			print event
		self.filterForKnownVenues()

		self.generateListOfArtists()	
	
	def findEvents(self, searchArgs):
		# Craft the search query
		eventfulEndpoint = self.assembleRequest(searchArgs)
		
		# Submit the search query 
		response = self.sendRequest(eventfulEndpoint)
		
		# parse the events into a list of Event objects
		for event in self.buildEvents(response):
			self.upcomingEvents.append(event)
		
		

	def assembleRequest(self, searchArgs):
		'''Receives search parameters and returns a URL for the endpoint'''
		
		filters = ['category=music', #seems to return the same results for music or concerts, so this might be unnecessary
							 'location=%s' %searchArgs['location'],
							 'time=%s' %searchArgs['time'],
							 'page_size=%s' %searchArgs['nResults'],
							 'page_number=%s' %searchArgs['page_number']]

		EVENTFUL_KEY = 'xmwwM432wt4KZF5c'	
		baseURL = 'http://api.eventful.com/json/events/search?app_key=%s' % EVENTFUL_KEY
			
		URL = baseURL	
		for f in filters:
			URL += '&' + f
		return URL

	def sendRequest(self, endpoint):
		# Hit the server and generate list of upcoming events
		print "Sending request: " + endpoint
		resp = requests.get(endpoint)
		if (resp.status_code != 200):
			raise UnexpectedStatusCode("Bad response from server. Status code: %i" %resp.status_code)
		if not resp.ok:
			raise BadResponse("Server Response Not OK")
		return resp.json()

	def buildEvents(self, json_response):
		numResults = int(json_response['total_items'])
		print numResults
		if numResults > 0:
			try:
				for event_dict in json_response['events']['event']:
					yield Event(event_dict)
			except:
				print json_response
				print "\n\n"

	def filterForKnownVenues(self):
		'''Reduces the upcomingEvents list down to just a list of events at known venues. An attempt to filter for concerts'''

		
		self.filteredUpcomingEvents = []
		for event in self.upcomingEvents:
			for venue in self.validVenues:
				if venue in event.venue_name:
					if event not in self.filteredUpcomingEvents:
						self.filteredUpcomingEvents.append(event)
		print "Filtered events. %i of %i events are at one of the valid venues" % (len(self.filteredUpcomingEvents), len(self.upcomingEvents))
		print self.filteredUpcomingEvents

	def generateListOfArtists(self):
		self.artists = []
		self.unfilteredArtists = []

		for event in self.filteredUpcomingEvents:
			self.artists.append(event.title)
		for event in self.upcomingEvents:
			self.unfilteredArtists.append(event.title)


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




if __name__ == '__main__':
	searchArgs = {'location':'San+Francisco',
								'time': 'Next+14+days',
								'nResults': '100'}

	EF = EventFinder(searchArgs)
	print "\n\nFILTERED ARTISTS: "
	print EF.artists #list of artists, ready to go into Spotify searches

	print "\n\n\nUNFILTERED ARTISTS: "
	print EF.unfilteredArtists #list of artists, ready to go into Spotify searches