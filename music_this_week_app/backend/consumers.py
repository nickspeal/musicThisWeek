from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from urllib.parse import parse_qs
import time # TODO remove this once it's no longer needed

from . import eventFinder
from .spotifyHandler import SpotifySearcher, PlaylistCreator

# Instantiate object used for handling anonymous Spotify requests, i.e. searching
searcher = SpotifySearcher()

# Number of characters to strip off the playlist URL and call it a unique ID
PLAYLIST_ID_LENGTH = 22


class Search(SyncConsumer):
    """
        A background process used to search for concerts and populate a playlist
        Emits status update messages on a group channel named after the playlist ID
    """

    def _publish_update(self, progress, status):
        print(status)
        channel_group = self.playlist[-PLAYLIST_ID_LENGTH:]
        async_to_sync(get_channel_layer().group_send)(channel_group, {
            "type": "update",
            "progress": progress,
            "status": status,
            "playlist": self.playlist,
        })

    def start_search(self, message):
        self.playlist = message["playlist"]
        time.sleep(10) # Hack - Allow some time for the client to subscribe before publishing the first update.
        # Search for list of upcoming artists
        self._publish_update(5, "Searching for events")
        ef = eventFinder.EventFinder()
        ef.searchForEvents(message["search_args"])
        artists = ef.performers

        # Validate and filter artists
        self._publish_update(40, "Found {} artits. Checking which ones are on Spotify".format(len(artists)))
        artist_URIs = searcher.filter_list_of_artists(artists)

        # Create List of Songs (track URIs)
        self._publish_update(75, "{} artists are on spotify. Searching for the most popular songs from each.".format(len(artist_URIs)))
        song_list = searcher.get_song_list(artist_URIs, N=99, order='shuffled')

        self._publish_update(95, "{} songs are lined up. Now we're just combining them into a Spotify playlist.".format(len(song_list)))

        # Load PlaylistCreator
        playlist_creator = PlaylistCreator()
        playlist_creator.complete_login(message["token"])

        # Populate Playlist
        playlist_creator.add(self.playlist, song_list)

        self._publish_update(100, "Playlist complete")




class Subscribe(JsonWebsocketConsumer):
    """
        A Websocket used to subscribe to the status of a playlist
        Forwards messages out to the client if they are emitted for the specified playlist ID
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

        self._subscribe_to_playlist(playlist_id)
        self.accept()

    def update(self, content):
        """Forward update messages out on the current channel"""
        self.send_json(content)

    def disconnect(self, close_code):
        print("Websocket disconnected")
        self._unsubscribe()
