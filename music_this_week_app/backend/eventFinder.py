#!/usr/bin/python
"""
Crawl the web for upcoming concerts and return a list of artists
musicThisWeek
Nick Speal 2016
"""

from collections import namedtuple
from datetime import datetime
import os
import time

import grequests
import requests

EVENTFUL_RESULTS_PER_PAGE = 50  # (I think it is max 100, default 20)

EVENTFUL_KEY = os.getenv('EVENTFUL_KEY')
if not EVENTFUL_KEY:
    raise Exception("Bad Eventful Key: " + str(EVENTFUL_KEY))


def time_ms():
    return int(round(time.time() * 1000))


def check_response(response):
    status_code = response.status_code

    try:
        response_json = response.json()
    except ValueError:
        print("Unable to parse JSON from server for %s response: %s" % (url, response))
        return None

    if not response.ok:
        print("Server response Not OK. \n  Sent request: %s \n  Status code: %i" % (url, status_code))
        print(response_json)
        return None
    if (status_code != 200):
        print("Bad response from server. \n  Sent request: %s \n  Status code: %i" % (url, status_code))
        print(response)
        return None
    if response_json is None:
        print("ERROR: could not search Eventful for url %s" % (url))
        return None
    if response.headers.get('Content-length') == '0':
        print ("No content from Eventful for request: " + url)
        return None

    return response


class EventFinder(object):
    def __init__(self):
        self.artists = []
        self.performers = []
        self.searchArgs = {}
        self.upcomingEvents = [] #A list of Event objects

    def get_total_pages_to_search(self, search_args):
        """ Check the result count for the desired search args """
        url = self.assembleRequest(search_args, pageNum=1, count_only=True)

        start_ms = time_ms()
        print('Request to %s' % url)
        response = requests.get(url)
        print('Request to ' + url + ' took ' + str(time_ms() - start_ms) + ' ms')

        if check_response(response) is None:
            print("ERROR: No response from eventful.")
            return 0

        total_available = int(response.json().get('total_items', 0))
        total_requested = int(search_args.get('nResults'))
        total_events = min([total_available, total_requested])

        return total_events / EVENTFUL_RESULTS_PER_PAGE + 1

    def store_events(self, responses, total_pages):
        for page, response in enumerate(responses, start=1):
            if check_response(response) is None:
                break
            if page > total_pages:
                break
            json = response.json()
            if json.get('events') is None:
                print("ERROR: No eventful results for page %d" % page)
            else:
                # parse the events into a list of Event objects
                events = map(Event, json['events']['event'])
                self.upcomingEvents.extend(events)

    def searchForEvents(self, search_args):
        """
        Called by an external master, triggers a search

        Saves self.artists, self.upcomingEvents

        :param search_args: Dict of eventful arguments. nResults is max number of events
        :return:
        """
        print('Checking how many pages to crawl...')
        pages = self.get_total_pages_to_search(search_args)
        urls = [self.assembleRequest(search_args, p) for p in range(1, pages + 1)] 

        print('Crawling %d pages from the eventful api...' % pages)
        start_ms = time_ms()
        responses = grequests.map(grequests.get(u) for u in urls)
        print('Crawling took ' + str(time_ms() - start_ms) + ' ms')

        self.store_events(responses, pages)

        print ("Done searching for events. Saved %i events matching the search query" % len(self.upcomingEvents) )
        self.generateListOfArtists()

    def assembleRequest(self, searchArgs, pageNum, count_only = False):
        '''Receives search parameters and returns a URL for the endpoint'''

        filters = [ '',
                    'category=music', #seems to return the same results for music or concerts, so this might be unnecessary
                    'location=%s' %searchArgs['location'],
                    'date=%s' %searchArgs['date'],
                    'page_size=%s' %EVENTFUL_RESULTS_PER_PAGE,
                    'page_number=%s' %pageNum,
                    'sort_order=popularity' #Customer Support says this should work but I see no evidence of it working
                   ]
        filterString = '&'.join(filters + ['count_only=true'] if count_only else filters)


        baseURL = 'http://api.eventful.com/json/events/search?app_key=%s' % EVENTFUL_KEY

        URL = baseURL + filterString

        return URL

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
