from django.test import TestCase

import music_this_week_app.backend.eventFinder as eventFinder

class test_event_finder(TestCase):
    def setUp(self):
        self.search_args = {'location': 'San+Francisco',
                       'time': 'next+7+days',
                       'nResults': '5'}

    def test_init(self):
        """test initialization of the class"""
        # Search for list of upcoming artists
        EF = eventFinder.EventFinder(self.search_args)