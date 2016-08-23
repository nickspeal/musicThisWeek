"""
Main backend master that handles all the high level logic for execution.
This keeps views.py lightweight.
"""

import eventFinder
from spotifyHandler import SpotifySearcher

# Instantiate object used for handling Spotify requests without authorization, i.e. searching
searcher = SpotifySearcher()


def execute(playlist_creator, search_args):
    """
    Main Search and Create Playlist Flow

    :param playlist_creator: spotifyHandler.PlaylistCreator object. Should be already logged in
    :param search_args: dict of search arguments for eventful
    :return playlistURL: URL for the spotify playlist. None if one was not created
    :return error: Error message, None if not applicable
    """

    # Validate user is logged in
    if not playlist_creator.is_logged_in():
        return None, "Error: User is not logged in"

    # Search for list of upcoming artists
    ef = eventFinder.EventFinder()
    ef.searchForEvents(search_args)
    artists = ef.performers

    # Validate and filter artists
    print("Searching for %i artists on Spotify..." % len(artists))
    artist_uris = searcher.filter_list_of_artists(artists)
    if len(artist_uris) == 0:
        return None, "No results found."

    # Create List of Songs (track URIs)
    print ("%i artists found on Spotify. Creating a playlist..." % len(artist_uris))
    song_list = searcher.get_song_list(artist_uris, N=99, order='shuffled')

    # Get Playlist ID
    (playlist_url, playlist_uri) = playlist_creator.get_spotify_playlist("musicThisWeek")

    # Populate Playlist
    playlist_creator.erase(playlist_url)
    playlist_creator.add(playlist_url, song_list)

    print("\n\nSuccessfully Created a playlist! Give it a listen:")
    print(playlist_url)

    context = {
        'playlist_url': playlist_url,
        'embed_url': 'https://embed.spotify.com/?uri=%s' % playlist_uri,
    }

    return context, None
