from django.test import TestCase

from music_this_week_app.backend.playlistCreator import PlaylistCreator
import music_this_week_app.backend.eventFinder as eventFinder

class test_integration(TestCase):
    def setUp(self):
        self.search_args = {'location': 'San+Francisco',
                       'time': 'next+7+days',
                       'nResults': '5'}

    def test_integration(self):
        """test end to end flow"""
        # Instantiate

        pc = PlaylistCreator()
        pc.cli_login(username="nickspeal")

        # Search for list of upcoming artists
        EF = eventFinder.EventFinder(self.search_args)

        # Create a Spotify playlist with those artists
        url = pc.createPlaylist(EF.unfilteredArtists)

        print "\n\nSuccessfully Created a playlist! Give it a listen:"
        print url