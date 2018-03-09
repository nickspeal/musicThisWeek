from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync
import json

from ..backend import eventFinder
from ..backend.spotifyHandler import SpotifySearcher, get_playlist_id_from_url

# Instantiate object used for handling anonymous Spotify requests, i.e. searching
searcher = SpotifySearcher()

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

        channel_group = get_playlist_id_from_url(self.playlist)
        async_to_sync(self.channel_layer.group_send)(channel_group, message)

    def start_search(self, message):
        print("start search consumer called")
        self.playlist = message["playlist"]
        self.token = message["token"]

        # Add the current consumer to the group, so that messages about this playlist go to this SearchConsumer instance AND any subscribers
        # TODO perhaps this belongs in an __init__ method
        group_channel_name = get_playlist_id_from_url(self.playlist)
        current_consumer_channel_name = self.channel_name
        async_to_sync(self.channel_layer.group_add)(group_channel_name, current_consumer_channel_name)

        # Initialize the song consumer
        async_to_sync(self.channel_layer.send)('song', {
            'type': 'login',
            'playlist': self.playlist,
            'token': self.token,
        })

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
        pass

    def song_not_found(self, message):
        pass
