from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync

def get_playlist_id_from_url(url):
    """
        Utility function used in multiple places to read the last N digits off a Spotify playlist URL,
        obtaining a single playlist ID string that can be used to uniquely refer to it throughout this app.
    """

    # Number of characters to strip off the playlist URL and call it a unique ID
    PLAYLIST_ID_LENGTH = 22
    return url[-PLAYLIST_ID_LENGTH:]

class PlaylistGroupConsumer(SyncConsumer):
    """
        Abstract Consumer to serve as a base class for any consumer that subscribes to
        the channel named after a playlist
    """
    def subscribe_to_group(self, playlist):
        # Subscribe to the playlist group
        self.group_channel_name =  get_playlist_id_from_url(playlist)
        current_consumer_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(self.group_channel_name, current_consumer_channel_name)

    def broadcast_to_group(self, message):
        async_to_sync(self.channel_layer.group_send)(self.group_channel_name, message)

    def events_found(self, message):
        pass

    def song_found(self, message):
        pass

    def song_not_found(self, message):
        pass
