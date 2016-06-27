"""
Main backend master that handles all the high level logic for execution.
This keeps views.py lightweight.
"""

# import music_this_week_app.backend.eventFinder as eventFinder

import eventFinder
from spotifyHandler import SpotifySearcher


class Master(object):
    def __init__(self):
        self.searcher = SpotifySearcher()


    def logInToSpotify(self):
        pass

    def execute(self, playlist_creator, searchArgs):
        """
        Main Search and Create Playlist Flow

        :param playlist_creator: spotifyHandler.PlaylistCreator object. Should be already logged in
        :param searchArgs: dict of search arguments for eventful
        :return:
        """

        # Validate user is logged in
        if not playlist_creator.is_logged_in():
            raise Exception("ERROR: User is not logged in.")

        # Search for list of upcoming artists
        ef = eventFinder.EventFinder()
        ef.searchForEvents(searchArgs)
        artists = ef.artists

        print("Searching for %i artists on Spotify..." %len(artists))
        # Validate and filter artists
        artist_URIs = self.searcher.filter_list_of_artists(artists)
        if len(artist_URIs) == 0:
            raise Exception("Error: No matching artists found")
        print ("%i artists found on Spotify. Creating a playlist..." %len(artist_URIs))
        # Create List of Songs (track URIs)
        song_list = self.searcher.get_song_list(artist_URIs, N=99, order='shuffled')

        # Get Playlist ID
        playlistURL = playlist_creator.get_spotify_playlist("musicThisWeek")

        # Populate Playlist
        playlist_creator.erase(playlistURL)
        playlist_creator.add(playlistURL, song_list)

        print("\n\nSuccessfully Created a playlist! Give it a listen:")
        print(playlistURL)

        return playlistURL