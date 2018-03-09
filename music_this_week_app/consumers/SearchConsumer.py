from .PlaylistGroupConsumer import PlaylistGroupConsumer
from asgiref.sync import async_to_sync

from ..backend import eventFinder

ef = eventFinder.EventFinder()

class SearchConsumer(PlaylistGroupConsumer):
    """
        Responds to messages on the "Search" channel
        Uses EventFinder to search for shows and emits messages to the group whenever some are found
    """

    @staticmethod
    def _parse_message(message):
        playlist = message.get("playlist")
        token = message.get("token")
        if not playlist:
            print("Error: No playlist specified in start_search message")
        if not token:
            print("Error: No token specified in start_search message")
        return playlist, token

    def start_search(self, message):
        playlist, token = self._parse_message(message)

        # TODO rethink this - Maybe this is contained within the song consumer? Should it get the token from the playlist Model?
        # Initialize the song consumer
        async_to_sync(self.channel_layer.send)('song', {
            'type': 'init',
            'playlist': playlist,
            'token': token,
        })

        # Initialize the events consumer
        async_to_sync(self.channel_layer.send)('events', {
            'type': 'init',
            'playlist': playlist,
        })

        # Initialize self.
        self.subscribe_to_group(playlist)

        ef.searchForEvents(message["search_args"], onProgress=self._broadcast_events_found)

    def _broadcast_events_found(self, event_list):
        self.broadcast_to_group({
            "type": "events_found",
            "events": [e.to_json() for e in event_list],
        })
