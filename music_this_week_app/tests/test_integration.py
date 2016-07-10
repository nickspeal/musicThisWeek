from django.test import TestCase

import music_this_week_app.backend as backend
from music_this_week_app.backend.spotifyHandler import PlaylistCreator


class test_integrations(TestCase):
    def setUp(self):
        self.search_args = {'location': 'San+Francisco',
                       'date': 'next+7+days',
                       'nResults': '100'}

    def test_integration_end_to_end(self):
        """test end to end flow"""

        pc = PlaylistCreator()
        pc.cli_login("nickspeal")

        (url, error) = backend.execute(pc, self.search_args)
        print("Playlist Generated:")
        print(url)
        print("Error: " + error)
