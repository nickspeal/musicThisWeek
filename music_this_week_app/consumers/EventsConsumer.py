from .PlaylistGroupConsumer import PlaylistGroupConsumer
from asgiref.sync import async_to_sync
from ..backend.spotifyHandler import SpotifySearcher
import json

# Instantiate object used for handling anonymous Spotify requests, i.e. searching
searcher = SpotifySearcher()


class EventsConsumer(PlaylistGroupConsumer):
    """
        Responds to messages on the events channel or in the group defined by a playlist
    """
    def init(self, message):
        self.subscribe_to_group(message.get('playlist'))

    def events_found(self, message):
        """
            "Responds to messages of type 'events_found' in the playlist group
            When a list of events are found, check Spotify for each artist
            Checks for songs for each event and emits messages on the same group with type "song_found" or "song_not_found"
        """
        for event in message.get('events', []):
            artists = json.loads(event).get('artists', [])
            for artist in artists:
                songs = searcher.find_songs_for_artist(artist)
                if songs:
                    self.broadcast_to_group({
                        "type": "song_found",
                        "artist": artist,
                        "songs": songs,
                    })
                else:
                    self.broadcast_to_group({
                        "type": "song_not_found",
                        "artist": artist,
                    })
