import spotipy
from ..models import Artist
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials # For authenticating requests independent of user


VERBOSE = False

class SpotifySearcher(object):
    """Handles unauthenticated Spotify requests like searching for artists and songs"""

    def __init__(self):
        # Init anonymized Spotify handle
        client_credentials_manager = SpotifyClientCredentials()
        # This should be the only instance attribute, to maintain statelessness
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def find_songs_for_artist(self, artist_name):
        artistURI = self.filter_artist(artist_name)
        if artistURI is None:
            return None

        # Find 2 tracks per artist for now
        tracks = self.find_top_tracks(artistURI, 2)
        return tracks

    def filter_list_of_artists(self, unfiltered_artists):
        """
        Turn a list of potential artist names into a list of Spotify artist URIs
        Filter out artists that cannot be found from the list.

        :param unfiltered_artists: list of strings of artist names
        :return artistURIs: list of strings of verified Spotify artist identifiers
        """

        artistURIs = [self.filter_artist(a) for a in unfiltered_artists]
        artistURIs = [a for a in artistURIs if a is not None]
        if VERBOSE:
            print("\n%i of the %i artists were found on Spotify." % (len(artistURIs), len(unfiltered_artists)))
        return artistURIs

    def filter_artist(self, artist_name):
        """
        Matches an artist name to a Spotify Artist URI
        First checks the local database for a match and searches Spotify otherwise

        :param artist_name: string
        :return artistURI: Verified Spotify artist identifier. Return None if no match
        """

        # Check if the artist is in the database
        try:
            artist_entry = Artist.objects.get(name = artist_name)
            artist_uri = artist_entry.spotify_uri

        # If the artist isn't in the database, search Spotify
        except Artist.DoesNotExist:
            result = self.search_spotify(artist_name)

            # If there were any errors searching Spotify, don't continue
            if result is not None:
                artist_uri = self.filter_spotify_result(result, artist_name)
            else:
                artist_uri = None

            # Save artist URI to the database for faster results next time
            self.save_new_artist(artist_name, artist_uri)

        return artist_uri

    def search_spotify(self, artist_name):
        """
        Searches Spotify for an artist name and handles exceptions

        The Spotify result is a JSON object containing an array of artist objects called 'items'
        More info: https://developer.spotify.com/web-api/search-item/


        :param artist_name: string
        :return: Spotify result or None if an exception is raised.
        """
        if VERBOSE:
            print ("\nSearching for artist on Spotify: " + artist_name)
        try:
            result = self.sp.search(q='artist:' + artist_name, type='artist')
        except spotipy.client.SpotifyException:
            print("ERROR: Couldnt not find artist: %s. Trying again." % artist_name)
            try:
                result = self.sp.search(q='artist:' + artist_name, type='artist')
            except spotipy.client.SpotifyException as error:
                print("ERROR: Failed to search twice. Error below:")
                print(error)
                result = None
        except ValueError as error:
            print("ERROR: Failure while searching Spotify for artist: %s" % artist_name)
            print(error)
            result = None
        return result

    def filter_spotify_result(self, result, artist_name):
        """
        Given a Spotify result, which can contain multiple artists matching a search query,
        identify and return the URI for the artist that best matches the query.

        :param result: A result from Spotify API. More info: https://developer.spotify.com/web-api/search-item/
        :param artist_name: String
        :return artist_uri: String or None, the best artist_URI found or None if no artists in results
        """
        artists = result['artists']['items']  # list of dicts

        num_matches = int(result['artists']['total'])
        if num_matches == 0:
            if VERBOSE:
                print("No matches found!")
            artist_uri = None

        elif num_matches == 1:
            if VERBOSE:
                print ("1 match found: " + artists[0]['name'])
                if artists[0]['name'] == artist_name:
                    print ("Exact match!")
                else:
                    print ("Close enough...")
            artist_uri = artists[0]['uri']

        elif num_matches > 1:
            if VERBOSE:
                print ("%i matches found: " % num_matches + str([a['name'] for a in artists]) )

            # check for exact match
            no_exact_match = True
            for a in artists:
                if a['name'] == artist_name:
                    if VERBOSE:
                        print("Exact match found!")
                    artist_uri = a['uri']
                    no_exact_match = False
                    break
            # If there is no exact match, the first match is probably best.
            if no_exact_match:
                artist_uri = artists[0]['uri']

        return artist_uri

    def save_new_artist(self, artist_name, artist_uri):
        """
        saves artist name/uri pairs to DB
        :param artist_name: String
        :param artist_uri: String
        :return None:
        """

        Artist.objects.get_or_create(spotify_uri=artist_uri, name=artist_name)

    def get_song_list(self, artist_URIs, N=99, order="shuffled", onProgress=None):
        """
        Come up with a list of songs by a given list of artists

        :param artist_URIs: List of strings identifying Spotify Artists
        :param N: Desired length of the list
        :param order: Desired order of the list. Can be "shuffled". Other options may be added later
        :return tracklist: List of spotify track URIs, to create playlist later.
        """
        if len(artist_URIs) == 0:
            return []

        # Calculate number of tracks per artist. Round up to nearest int w/ int division then trim list later.
        number_of_tracks_per_artist = N // len(artist_URIs) + 1
        if number_of_tracks_per_artist > 10:
            print("Number of tracks per artist, %i, cannot be greater than 10." %number_of_tracks_per_artist)

        # Identify songs for the playlist; list of track URIs
        tracks = []
        for a in artist_URIs:
            tracks = tracks + self.find_top_tracks(a, N=number_of_tracks_per_artist)
            if onProgress:
                completion_fraction = len(tracks) / (number_of_tracks_per_artist * len(artist_URIs))
                onProgress(completion_fraction)

        if order == "shuffled":
            # Randomize playlist order
            shuffle(tracks)
            print("Prior to trimming, the playlist is %i songs long" %len(tracks))
            tracklist = tracks[0:N]
        else:
            raise Exception("Invalid song list order specified")

        return tracklist

    def find_top_tracks(self, artist, N=10):
        """
        Return top N tracks by one artist

        :param artist: URI
        :param N: maximum number of tracks to return. Cannot be greater than 10
        :return: list of track URIs
        """
        tracklist = []
        try:
            result = self.sp.artist_top_tracks(artist)
        except ConnectionError as e:
            print ("ERROR: connection pool is closed; searching Spotify for top tracks for this artist: " + artist)
            result = self.sp.artist_top_tracks(artist)
            print ("tried again")
            print (result)
            raise e

        for track in result['tracks']:
            tracklist.append(track['uri'])
        if len(tracklist) > N:
            return tracklist[0:N]
        else:
            return tracklist
