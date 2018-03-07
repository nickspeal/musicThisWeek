from channels.consumer import SyncConsumer
from . import eventFinder
from .spotifyHandler import SpotifySearcher, PlaylistCreator

# Instantiate object used for handling Spotify requests without authorization, i.e. searching
searcher = SpotifySearcher()

class SearchConsumer(SyncConsumer):
    def search(self, message):
        print("Searching!")
        # Search for list of upcoming artists
        ef = eventFinder.EventFinder()
        ef.searchForEvents(message["search_args"])
        artists = ef.performers

        # Validate and filter artists
        print("Searching for %i artists on Spotify..." % len(artists))
        artist_URIs = searcher.filter_list_of_artists(artists)
        if len(artist_URIs) == 0:
            return None, "No results found."

        # Create List of Songs (track URIs)
        print ("%i artists found on Spotify. Creating a playlist..." % len(artist_URIs))
        song_list = searcher.get_song_list(artist_URIs, N=99, order='shuffled')

        # Load PlaylistCreator
        playlist_creator = PlaylistCreator()
        playlist_creator.complete_login(message["token"])

        # Populate Playlist
        playlist_creator.add(message["playlist"], song_list)

        print("\n\nSuccessfully Created a playlist! Give it a listen:")
        print(message["playlist"])
