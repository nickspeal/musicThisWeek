from .PlaylistGroupConsumer import PlaylistGroupConsumer
from asgiref.sync import async_to_sync
from ..SpotifyHandler.SpotifySearcher import SpotifySearcher
import json

# Instantiate object used for handling anonymous Spotify requests, i.e. searching
searcher = SpotifySearcher()

def construct_playlist_items(artist, event_dict):
    songs = []
    for song in artist.get_songs():
        item = {"song": song.to_dict(), "artist": artist.to_dict(), "event": event_dict}
        songs.append(item)
    return songs

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
        for event_dict in message.get('events', []):
            artists = event_dict.get('artists', [])
            for artist_name in artists:
                artist = searcher.query_artist(artist_name)
                if artist:

                    playlist_items = construct_playlist_items(artist, event_dict)
                    self.broadcast_to_group({
                        "type": "songs_found",
                        "songs": playlist_items,
                    })
                else:
                    self.broadcast_to_group({
                        "type": "artist_not_found",
                        "artist": artist_name,
                    })
