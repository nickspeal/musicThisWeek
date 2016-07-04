from django.test import TestCase

from music_this_week_app.backend.spotifyHandler import PlaylistCreator
from music_this_week_app.backend import Master

class test_integrations(TestCase):
    def setUp(self):
        self.search_args = {'location': 'San+Francisco',
                       'date': 'next+7+days',
                       'nResults': '100'}
        self.master = Master()

    def test_integration_end_to_end(self):
        """test end to end flow"""

        pc = PlaylistCreator()
        pc.cli_login("nickspeal")

        url = self.master.execute(pc, self.search_args)
        print "Playlist Generated:"
        print url