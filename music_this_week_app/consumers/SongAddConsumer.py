from .PlaylistGroupConsumer import PlaylistGroupConsumer
from ..backend.spotifyHandler import PlaylistCreator, get_playlist_id_from_url

class SongAddConsumer(PlaylistGroupConsumer):
    """
        Responds to messages in the "song" channel and the playlist group after subscription
        Adds songs to Spotify Playlist if they are found.
    """
    def init(self, message):
        # Log in to Spotify
        self.playlist = message.get('playlist')
        self.playlist_creator = PlaylistCreator()
        self.playlist_creator.complete_login(message.get('token'))

        self.subscribe_to_group(self.playlist)

    def song_found(self, message):
        """Add songs to spotify playlist."""
        # TODO modify PlaylistCreator to save self.playlit itself on construction?
        self.playlist_creator.add(self.playlist, message.get('songs'))

    def song_not_found(self, message):
        print("No songs found for artist: ", message.get('artist'))
