"""
Main backend master that handles all the high level logic for execution.
This keeps views.py lightweight.
"""

import eventFinder
from spotifyHandler import SpotifySearcher



def execute(playlist_creator, search_args):
    """
    Main Search and Create Playlist Flow

    :param playlist_creator: spotifyHandler.PlaylistCreator object. Should be already logged in
    :param search_args: dict of search arguments for eventful
    :return playlistURL: URL for the spotify playlist. None if one was not created
    :return error: Error message, None if not applicable
    """
    #for each search request we instantiate a spotify searcher object  
    searcher = SpotifySearcher()
    # Validate user is logged in
    if not playlist_creator.is_logged_in():
        return None, "Error: User is not logged in"

    # Search for list of upcoming artists
    ef = eventFinder.EventFinder()
    ef.searchForEvents(search_args)
    artists = ef.performers

    # Validate and filter artists
    print("Searching for %i artists on Spotify..." % len(artists))
    searcher.fill_artist_lists(artists)
    num_uris = searcher.get_number_uris_found()   
    if num_uris == 0:
        return None, "No results found."

    # Create List of Songs (track URIs)
    print ("%i artists found on Spotify. Creating a playlist..." % num_uris)
    song_list = searcher.assemble_track_list(N=99, order='shuffled')

    # Get Playlist ID
    playlistURL = playlist_creator.get_spotify_playlist("musicThisWeek")

    # Populate Playlist
    playlist_creator.erase(playlistURL)
    playlist_creator.add(playlistURL, song_list)

    print("\n\nSuccessfully Created a playlist! Give it a listen:")
    print(playlistURL)

    return playlistURL, None
