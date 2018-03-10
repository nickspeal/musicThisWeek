#!/usr/bin/python
"""
Crawl the web for upcoming concerts and return a list of artists
musicThisWeek
Nick Speal 2016
"""

from datetime import datetime
import os
import time

import requests
import re
import json


EVENTFUL_RESULTS_PER_PAGE = 50  # (I think it is max 100, default 20)

EVENTFUL_KEY = os.getenv('EVENTFUL_KEY')
if not EVENTFUL_KEY:
    raise Exception("Bad Eventful Key: " + str(EVENTFUL_KEY))


def time_ms():
    return int(round(time.time() * 1000))


def request_was_successful(response):
    """ Checks if the request succeeded, returns a boolean. """
    status_code = response.status_code
    try:
        response_json = response.json()
    except ValueError:
        print("Unable to parse JSON from server for %s response: %s" % (response.url, response))
        return False
    if not response.ok:
        print("Server response Not OK. \n  Sent request: %s \n  Status code: %i" % (response.url, status_code))
        print(response_json)
        return False
    if (status_code != 200):
        print("Bad response from server. \n  Sent request: %s \n  Status code: %i" % (response.url, status_code))
        print(response)
        return False
    if response_json is None:
        print("ERROR: could not search Eventful for url %s" % (response.url))
        return False
    if response.headers.get('Content-length') == '0':
        print ("No content from Eventful for request: " + response.url)
        return False
    return True

def parseDate(start, end):
    """
    Converts the start and end dates from the HTML widget into eventful format
    :param start: String, search range start date with format YYYY-MM-DD
    :param end: String, search range end date with format YYYY-MM-DD
    :return parsedDate: String, search range with format YYYYMMDD00-YYYYMMDD00
    """
    return re.sub('-', '', start) + '00-' + re.sub('-','', end) + '00'

class EventFinder(object):
    def __init__(self):
        self.artists = []
        self.performers = []
        self.searchArgs = {}
        self.upcomingEvents = [] #A list of Event objects

    @staticmethod
    def get_total_pages_to_search(search_args):
        """ Check the result count for the desired search args """
        url = EventFinder.assembleRequest(search_args, pageNum=1, count_only=True)

        start_ms = time_ms()
        response = requests.get(url)
        print("[EventFinder]: Total page count request took {} ms".format(time_ms() - start_ms))

        if not request_was_successful(response):
            print("ERROR: No response from eventful.")
            return 0

        total_available = int(response.json().get('total_items', 0))
        total_requested = int(search_args.get('nResults'))
        total_events = min([total_available, total_requested])

        return total_events // EVENTFUL_RESULTS_PER_PAGE + 1

    @staticmethod
    def parse_events(response):
        """ Returns a list of Events parsed from the eventful API """

        if not request_was_successful(response):
            print('WARNING: Unsuccessful HTTP response from eventful')
            return []

        json = response.json()
        if json.get('events') is None:
            print("ERROR: No eventful results on page")
            return []

        # parse the events into a list of Event objects
        # print(json)
        events = []
        events.extend(map(Event, json['events']['event']))
        return events

    def searchForEvents(self, search_args, onProgress):
        """
        Called by an external master, triggers a search

        Saves self.artists, self.upcomingEvents

        :param search_args: Dict of eventful arguments. nResults is max number of events
        :return:
        """
        print('[EventFinder]: Search For Events called. Checking how many pages to crawl...')
        pages = self.get_total_pages_to_search(search_args)
        urls = [self.assembleRequest(search_args, p) for p in range(1, pages + 1)]

        print('[EventFinder]: Crawling %d pages from the eventful api...' % pages)
        start_ms = time_ms()

        for u in urls:
            response = requests.get(u)
            events = self.parse_events(response)
            onProgress(events)

        print('[EventFinder]: Crawling took ' + str(time_ms() - start_ms) + ' ms')


    @staticmethod
    def assembleRequest(searchArgs, pageNum, count_only=False):
        """Receives search parameters and returns a URL for the endpoint

        :param searchArgs: Dictionary of eventful search arguements
        :param pageNum: Eventful page number
        :param count_only: Flag for returning all results or just the number of results
        :return URL: Eventful endpoint with the appropriate parameters
        """
        filters = [ '',
                    'category=music', #seems to return the same results for music or concerts, so this might be unnecessary
                    'location=%s' %searchArgs['location'],
                    'date=%s' %parseDate(searchArgs['start'], searchArgs['end']),
                    'page_size=%s' %min(EVENTFUL_RESULTS_PER_PAGE, int(searchArgs['nResults'])),
                    'page_number=%s' %pageNum,
                    'sort_order=popularity' #Customer Support says this should work but I see no evidence of it working
                   ]
        filterString = '&'.join(filters + ['count_only=true'] if count_only else filters)
        baseURL = 'http://api.eventful.com/json/events/search?app_key=%s' % EVENTFUL_KEY
        URL = baseURL + filterString
        return URL


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

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "date": self.date.strftime('%m/%d/%Y'),
            "venue": self.venue_name,
            "artists": self.performers, # TODO sometimes this list is empty. Use title instead.
            "url": self.url,
        }
