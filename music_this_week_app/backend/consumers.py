from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from urllib.parse import parse_qs
import json

from . import eventFinder
from .spotifyHandler import SpotifySearcher, PlaylistCreator

# Instantiate object used for handling anonymous Spotify requests, i.e. searching
searcher = SpotifySearcher()

# Number of characters to strip off the playlist URL and call it a unique ID
PLAYLIST_ID_LENGTH = 22

class SearchConsumer(SyncConsumer):
    """
        Instantiated each time a search is conducted (When the /create View sends an event on the "search" channel)
        Executed by the worker process
    """

    def __init__(self, _):
        self.playlist = None
        self.token = None
        self.playlist_creator = None
        super().__init__(_)

    def _broadcast_to_group(self, message):
        channel_group = self.playlist[-PLAYLIST_ID_LENGTH:]
        async_to_sync(self.channel_layer.group_send)(channel_group, message)

    def start_search(self, message):
        print("start search consumer called")
        self.playlist = message["playlist"]
        self.token = message["token"]

        # Add the current consumer to the group, so that messages about this playlist go to this SearchConsumer instance AND any subscribers
        # TODO perhaps this belongs in an __init__ method
        group_channel_name = self.playlist[-PLAYLIST_ID_LENGTH:]
        current_consumer_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(group_channel_name, current_consumer_channel_name)

        # Search for list of upcoming artists
        ef = eventFinder.EventFinder()
        ef.searchForEvents(message["search_args"], onProgress=self._broadcast_events_found)

    def _broadcast_events_found(self, event_list):
        message = {
            "type": "events_found",
            "events": [e.to_json() for e in event_list],
            "playlist": self.playlist, # no longer Duplicate info from channel group?
        }
        self._broadcast_to_group(message)

    def events_found(self, message):
        """
            When a list of events are found, check Spotify for each artist
            Checks for songs for each event and emits messages on the same group with type "song_found" or "song_not_found"
        """
        for event in message.get('events', []):
            artists = json.loads(event).get('artists', [])
            for artist in artists:
                songs = searcher.find_songs_for_artist(artist)
                if songs:
                    self._broadcast_to_group({
                        "type": "song_found",
                        "artist": artist,
                        "songs": songs,
                    })
                else:
                    self._broadcast_to_group({
                        "type": "song_not_found",
                        "artist": artist,
                    })

    def song_found(self, message):
        """Add songs to spotify playlist. Log in the first time."""
        print("song found: ", message)
        if not self.playlist_creator:
            self.playlist_creator = PlaylistCreator()
            self.playlist_creator.complete_login(self.token)
        self.playlist_creator.add(self.playlist, message.get('songs'))

    def song_not_found(self, content):
        print("song not found", content)
        # TODO maybe remove the artist from the playlist DB or something
        # I need this placeholder for now so that there is some receipient of the message in the group if the client disconnects.
        pass


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
        playlist_id = playlist[-PLAYLIST_ID_LENGTH:]
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
