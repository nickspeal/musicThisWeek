import spotipy

class SpotifyUser():
    def __init__(self, token):
        self.sp = spotipy.Spotify(auth=token)
        try:
            # sp.me() returns the following info: product, display_name, external_urls, country, uri, id, href, followers, images (list of dicts with these keys): (url, width, height), type, email
            # interesting stuff might be id, display_name, external_urls.spotify, images[0].url (doesn't exist for non-fb users), email
            self.user = self.sp.me()
        except spotipy.client.SpotifyException:
            self.user = None

    def _find_matching_playlists(self, playlists, title):
        for playlist in playlists['items']:
            if playlist['name'] == title:
                return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

        # Create new playlist if needed
        playlist = self.sp.user_playlist_create(self.user.get('id'), title)
        return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

    def _erase_playlist(self, playlist_url):
        self.sp.user_playlist_replace_tracks(self.user.get('id'), playlist_url, [])

    def is_token_valid(self):
        if self.user is None:
            return False
        else:
            return True

    # Not sure about the encoding here...
    def to_json(self):
        return self.user

    def get_spotify_playlist(self, title="Music This Week", erase=False):
        """
        Returns a playlist URL matching a user's playlist with a specified name.
        Creates the playlist if it doesn't exist yet.

        :param title: Playlist name
        :return: Playlist URL (Not URI - it should load in the browser)
        """
        if self.is_token_valid():
            # Check if playlist already exists
            users_playlists = self.sp.user_playlists(self.user.get('id'))
            playlist_url = self._find_matching_playlists(users_playlists, title)
            if erase:
                self._erase_playlist(playlist_url)
            return playlist_url

        else:
            raise Exception("User Is Not Logged In")
