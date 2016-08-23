from django.test import TestCase

import music_this_week_app.backend as backend
from music_this_week_app.backend.spotifyHandler import PlaylistCreator


class test_integrations(TestCase):
    def setUp(self):
        self.search_args = {'location': 'San+Francisco',
                            'start': '2016082100',
                            'end': '2016082800',
                            'nResults': '100'}

    def test_integration_end_to_end(self):
        """test end to end flow"""

        pc = PlaylistCreator()
        pc.cli_login("nickspeal_test")

        (url, error) = backend.execute(pc, self.search_args)
        print("Playlist Generated:")
        print(url)
        if error:
            print("Error: " + error)
        else:
            print("No Errors returned from backend.execute")
