from django.test import TestCase

from music_this_week_app.backend.eventFinder import (Event,
    EventFinder, request_was_successful)

# class test_event_finder(TestCase):
#     def setUp(self):
#         self.search_args = {'location': 'San+Francisco',
#                        'date': 'next+7+days',
#                        'nResults': '5'}
#
#     def test_init(self):
#         """test initialization of the class"""
#         # Search for list of upcoming artists
#         EF = eventFinder.EventFinder(self.search_args)


class ResponseStub(object):

    def __init__(self, _json=None, headers=None, ok=True, status_code=200, url=None):
        if _json is None:
            _json = {}
        self._json = _json
        if headers is None:
            headers = {}
        self.headers = headers
        self.ok = ok
        self.status_code = status_code
        self.url = url

    def json(self):
        return self._json


class EventFinderUnitTestCase(TestCase):

    def test_request_was_successful(self):
        self.assertEqual(request_was_successful(ResponseStub()), True)
        self.assertEqual(request_was_successful(ResponseStub(ok=False)), False)
        self.assertEqual(request_was_successful(ResponseStub(status_code=500)), False)
        self.assertEqual(request_was_successful(ResponseStub(ok=False, _json={})), False)

    def test_parse_events(self):
        event_dict = {
            'url': 'http://foo.com',
            'description': 'bar',
            'id': 0,
            'title': 'foo',
            'performers': {'performer': [{'name': 'Bono'}]},
            'venue_name': 'the foo bar',
            'venue_address': '1 foo st',
            'latitude': "37.7784991",
            'longitude': "100",
            'start_time': "2016-07-19 19:30:00",
        }
        event_json = {'events': {'event': [event_dict]}}
        response = ResponseStub(_json=event_json)
        events = EventFinder.parse_events([response], 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(type(events[0]), Event)
        self.assertEqual(events[0].performers, ['Bono'])

# To Test
# How many results per page
# What are the names like from eventful
# Are all the results in the specified search range?
