from django.test import TestCase

from music_this_week_app.backend.playlistCreator import PlaylistCreator


class test_Spotify(TestCase):
    def setUp(self):
        self.pc = PlaylistCreator()

    def test_login(self):

        self.pc.cli_login(username="nickspeal")

    def test_createPlaylist(self):

        self.pc.cli_login(username="nickspeal")
        artists = ["The Hives", "U2"]
        url = self.pc.createPlaylist(artists)
        print(url)
