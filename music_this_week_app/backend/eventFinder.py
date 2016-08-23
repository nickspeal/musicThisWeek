#!/usr/bin/python
"""
Crawl the web for upcoming concerts and return a list of artists
musicThisWeek
Nick Speal 2016
"""

import requests
import os
from datetime import datetime
import re

EVENTFUL_RESULTS_PER_PAGE = 50  # (I think it is max 100, default 20)

EVENTFUL_KEY = os.getenv('EVENTFUL_KEY')
if not EVENTFUL_KEY:
    raise Exception("Bad Eventful Key: " + str(EVENTFUL_KEY))

class EventFinder(object):
    def __init__(self):
        self.artists = []
        self.performers = []
        self.searchArgs = {}
        self.upcomingEvents = [] #A list of Event objects

    def searchForEvents(self, searchArgs):
        """
        Called by an external master, triggers a search

        Saves self.artists, self.upcomingEvents

        :param searchArgs: Dict of eventful arguments. nResults is max number of events
        :return:
        """

        # Check the result count for the desired search args
        url = self.assembleRequest(searchArgs, pageNum=1, count_only=True)
        response = self.sendRequest(url)
        if response is None:
            print ("ERROR: No response from eventful")
            return

        number_of_available_results = int(response.get('total_items', 0))
        number_of_requested_results = int(searchArgs.get('nResults'))

        # Determine how many pages are needed, integer division
        if number_of_available_results == 0:
            return
        elif number_of_available_results >= number_of_requested_results:
            nPages = number_of_requested_results // EVENTFUL_RESULTS_PER_PAGE + 1
        else:
            nPages = number_of_available_results // EVENTFUL_RESULTS_PER_PAGE + 1

        for pageNum in range(1,nPages+1):
            # Assemble the Search Querie
            url = self.assembleRequest(searchArgs, pageNum)

            # Submit the search query
            response = self.sendRequest(url)
            if response is None:
                print("ERROR: could not search Eventful for page %i of %i" % (pageNum, nPages))
                continue
            elif response.get('events') is None:
                print("ERROR: No eventful results for page %i of %i" % (pageNum, nPages))
                continue
            # parse the events into a list of Event objects
            for event in self.buildEvents(response):
                self.upcomingEvents.append(event)

        print ("Done searching for events. Saved %i events matching the search query" % len(self.upcomingEvents) )
        self.generateListOfArtists()

    def assembleRequest(self, searchArgs, pageNum, count_only = False):
        """
        Receives search parameters and returns a URL for the endpoint

        :param searchArgs: Dictionary of eventful search arguements
        :param pageNum: Eventful page number
        :param count_only: Flag for returning all results or just the number of results
        :return URL: Eventful endpoint with the appropriate parameters
        """
        filters = [ '',
                    'category=music', #seems to return the same results for music or concerts, so this might be unnecessary
                    'location=%s' %searchArgs['location'],
                    'date=%s' %self.parseDate(searchArgs['start'], searchArgs['end']),
                    'page_size=%s' %EVENTFUL_RESULTS_PER_PAGE,
                    'page_number=%s' %pageNum,
                    'sort_order=popularity' #Customer Support says this should work but I see no evidence of it working
                   ]
        filterString = '&'.join(filters + ['count_only=true'] if count_only else filters)
        baseURL = 'http://api.eventful.com/json/events/search?app_key=%s' % EVENTFUL_KEY
        URL = baseURL + filterString
        return URL

    def parseDate(self, start, end):
        """
        Converts the start and end dates from the HTML widget into eventful format
        :param start: String, search range start date with format YYYY-MM-DD
        :param end: String, search range end date with format YYYY-MM-DD
        :return parsedDate: String, search range with format YYYYMMDD00-YYYYMMDD00
        """
        return re.sub('-', '', start) + '00-' + re.sub('-','', end) + '00'

    def sendRequest(self, endpoint):
        """Send the search query to Eventful"""
        print ("Sending request: " + endpoint)
        resp = requests.get(endpoint)

        if (resp.status_code != 200):
            print("Bad response from server. \n  Sent request: %s \n  Status code: %i" % (endpoint, resp.status_code))
            print(resp.json())
            return None
        if not resp.ok:
            print("Server response Not OK. \n  Sent request: %s \n  Status code: %i" % (endpoint, resp.status_code))
            print(resp.json())
            return None
        if resp.headers.get('Content-length') == '0':
            print ("No content from Eventful for request: " + endpoint)
            return None
        return resp.json()

    def buildEvents(self, json_response):
        for event_dict in json_response['events']['event']:
            yield Event(event_dict)

    def generateListOfArtists(self):
        for event in self.upcomingEvents:
            self.artists.append(event.title)
            self.performers += event.performers

class Event(object):
    def __init__(self, event_dict):
        self.url = event_dict['url']
        self.description = event_dict['description']
        self.id = event_dict['id']

        self.title = event_dict['title']
        self.performers = []
        # Performers will be None or a dict or a list of dicts
        # Each must be treated differently:
        if event_dict['performers'] is None:
            pass
        else:
            p = event_dict['performers']['performer']
            if type(p) is dict:
                self.performers.append(p['name'])
            elif type(p) is list:
                for item in p:
                    self.performers.append(item['name'])
            else:
                print (type(p))
                print (p)
                raise Exception("Performers are formatted weirdly")

        self.venue_name = event_dict['venue_name']
        self.venue_address = event_dict['venue_address']
        self.latitude = event_dict['latitude']  # "37.7784991"
        self.longitude = event_dict['longitude']
        self.date = event_dict['start_time']  # "2016-07-19 19:30:00"
        self.date = datetime.strptime(self.date, "%Y-%m-%d  %H:%M:%S")
    def __repr__(self):
        return "Title: %r \nVenue: %r" % (self.title, self.venue_name)

