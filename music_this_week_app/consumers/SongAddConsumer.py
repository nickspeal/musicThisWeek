from channels.consumer import SyncConsumer
from ..backend.spotifyHandler import PlaylistCreator, get_playlist_id_from_url
from asgiref.sync import async_to_sync

class SongAddConsumer(SyncConsumer):
    def login(self, message):
        print('logging in to spotify')
        self.playlist = message.get('playlist')
        self.playlist_creator = PlaylistCreator()
        self.playlist_creator.complete_login(message.get('token'))

        # Subscribe to the playlist group
        group_channel_name =  get_playlist_id_from_url(self.playlist)
        current_consumer_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(group_channel_name, current_consumer_channel_name)

    def song_found(self, message):
        """Add songs to spotify playlist."""
        self.playlist_creator.add(self.playlist, message.get('songs'))

    def song_not_found(self, message):
        pass

    def events_found(self, message):
        pass
