from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from urllib.parse import parse_qs
from ..backend.spotifyHandler import get_playlist_id_from_url

class Subscribe(JsonWebsocketConsumer):
    """
        A Websocket used to subscribe to the status of a playlist
        Forwards messages out to the client if they are emitted for the specified playlist ID
        Print statements here go in the main runserver terminal
    """
    def _subscribe_to_playlist(self, playlist):
        # Save this ID for the rest of the subscribtion so that we can disconnect later.
        self.playlist = playlist
        group_channel_name = self.playlist
        current_client_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(group_channel_name, current_client_channel_name)

    def _unsubscribe(self):
        group_channel_name = self.playlist
        current_client_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_discard)(group_channel_name, current_client_channel_name)

    def connect(self):
        qs = parse_qs(self.scope['query_string'].decode('UTF-8'))
        playlist = qs['playlist'][0]
        playlist_id = get_playlist_id_from_url(playlist)
        print("Websocket Connection received from client. self channel name is ", self.channel_name)
        self._subscribe_to_playlist(playlist_id)
        self.accept()

    """Forward update messages out on the current channel"""
    def update(self, content):
        self.send_json(content)

    def events_found(self, content):
        self.send_json(content)

    def song_found(self, content):
        self.send_json(content)

    def song_not_found(self, content):
        self.send_json(content)

    def disconnect(self, close_code):
        print("Websocket disconnected")
        self._unsubscribe()
