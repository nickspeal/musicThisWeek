from .PlaylistGroupConsumer import PlaylistGroupConsumer
from ..SpotifyHandler.SpotifyPlaylist import SpotifyPlaylist

class SongAddConsumer(PlaylistGroupConsumer):
    """
        Responds to messages in the "song" channel and the playlist group after subscription
        Adds songs to Spotify Playlist if they are found.
    """
    def init(self, message):
        # Log in to Spotify
        self.playlist = SpotifyPlaylist(message.get('token'), message.get('playlist'))
        self.subscribe_to_group(message.get('playlist'))

    def song_found(self, message):
        """Add songs to spotify playlist."""
        self.playlist.add(message.get('songs'))

    def song_not_found(self, message):
        print("No songs found for artist: ", message.get('artist'))
