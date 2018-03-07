"""
Main backend master that handles all the high level logic for execution.
This keeps views.py lightweight.
"""


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .spotifyHandler import PlaylistCreator

def execute(token, search_args):
    """
    Main Search and Create Playlist Flow

    :param playlist_creator: spotifyHandler.PlaylistCreator object. Should be already logged in
    :param search_args: dict of search arguments for eventful
    :return playlistURL: URL for the spotify playlist. None if one was not created
    :return error: Error message, None if not applicable
    """

    # Load PlaylistCreator
    playlist_creator = PlaylistCreator()
    playlist_creator.complete_login(token)

    # Validate user is logged in
    if not playlist_creator.is_logged_in():
        return None, "Error: User is not logged in"

    # Get Playlist ID
    playlistURL = playlist_creator.get_spotify_playlist("Music This Week")
    print("Playlist URL is", playlistURL)

    # Erase Playlist
    playlist_creator.erase(playlistURL)

    # TODO Search for artists and populate the playlist here!

    channel_layer = get_channel_layer()
    print("About to call background search task")
    async_to_sync(channel_layer.send)(
        "search",
        {
            "type": "search",
            "playlist": playlistURL,
            "search_args": search_args,
            "token": token,
        },
    )

    return playlistURL, None
