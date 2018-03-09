import spotipy
from .SpotifyUser import SpotifyUser

class SpotifyPlaylist():
    def __init__(self, token, playlist_url):
        """
        :param token:
        :param playlist_url: Playlist URL
        """
        self.sp = spotipy.Spotify(auth=token)
        self._check_logged_in(token)
        self.user_id = self.sp.me().get('id')
        self.playlist_url = playlist_url
        self.playlist = None

    def _check_logged_in(self, token):
        user = SpotifyUser(token)
        if not user.is_token_valid:
            raise Exception("Invalid token")

    def erase(self):
        """
        Replace an empty playlist

        :param playlist: Spotify Playlist URL (or URI - whatever)
        :return:
        """
        self.sp.user_playlist_replace_tracks(self.user_id, self.playlist_url, [])

    def add(self, song_list):
        """
        Adds a list of track IDs to a specified playlist ID

        :param playlist: Playlist URL (or URI, whatever)
        :param song_list: list of song URIs
        :return:
        """
        # Add songs to playlist 99 tracks at a time (Spotify limit)
        i=0
        while(i<len(song_list)):
            self.sp.user_playlist_add_tracks(self.username, playlist, song_list[i:i+99])
            i += 99
