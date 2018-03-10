from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from urllib.parse import parse_qs
from .PlaylistGroupConsumer import get_playlist_id_from_url

class Subscribe(JsonWebsocketConsumer):
    """
        A Websocket used to subscribe to the status of a playlist
        Forwards messages out to the client if they are emitted for the specified playlist ID
        Print statements here go in the main runserver terminal
    """
    def _subscribe_to_playlist(self, playlist_id):
        # Save this ID for the rest of the subscribtion so that we can disconnect later.
        print("Client Subscribed to playlist ", playlist_id)
        self.playlist_id = playlist_id
        group_channel_name = self.playlist_id
        current_client_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(group_channel_name, current_client_channel_name)

    def _unsubscribe(self):
        group_channel_name = self.playlist_id
        current_client_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_discard)(group_channel_name, current_client_channel_name)

    def connect(self):
        print("Websocket Connection received from client.")
        qs = parse_qs(self.scope['query_string'].decode('UTF-8'))
        playlist_id = get_playlist_id_from_url(qs['playlist'][0])
        self._subscribe_to_playlist(playlist_id)
        self.accept()

    """Forward update messages out on the current channel"""
    def events_found(self, content):
        self.send_json(content)

    def songs_found(self, content):
        self.send_json(content)

    def artist_not_found(self, content):
        self.send_json(content)

    def disconnect(self, close_code):
        print("Websocket disconnected")
        self._unsubscribe()
