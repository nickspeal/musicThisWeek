import spotipy
from ..models import Artist
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials # For authenticating requests independent of user
import json

VERBOSE = False
NUMBER_OF_SONGS_PER_ARTIST = 1

class SpotifySearcher(object):
    """Handles unauthenticated Spotify requests like searching for artists and songs"""

    def __init__(self):
        # Init anonymized Spotify handle
        client_credentials_manager = SpotifyClientCredentials()
        # This should be the only instance attribute, to maintain statelessness
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def query_artist(self, artist_name):
        """
        Given a potential artist name, return a fully populated Artist object or None if not found
        Includes top tracks
        First checks the local database for a match and searches Spotify otherwise

        :param artist_name: string
        "return Artist" an Artist object. See Models? Or None if not found.
        """
        # Check if the artist is in the database
        try:
            a = Artist.objects.get(searched_name = artist_name)
            return ArtistObject(searched_name=artist_name, db_model=a)

        # If the artist isn't in the database, search Spotify
        except Artist.DoesNotExist:
            print("Artist not found in database: ", artist_name)
            result = self.search_spotify(artist_name)

            # If there were any errors searching Spotify, don't continue
            if result is None:
                # SKIP FOR TEST NOW
                ArtistObject(searched_name=artist_name).save_to_db()
                return None
            else:
                artist = self.filter_spotify_result(result, artist_name)

            if artist is None:
                ArtistObject(searched_name=artist_name).save_to_db()
                return None

            top_tracks = self.find_top_tracks(artist.uri)
            artist.add_songs(top_tracks)

            # Save artist URI to the database for faster results next time
            print("About to save artist with name {} and object: ".format(artist_name), artist)
            artist.save_to_db()

        return artist

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
        identify and a dict for the artist that best matches the query.

        :param result: A result from Spotify API. More info: https://developer.spotify.com/web-api/search-item/
        :param artist_name: String
        :return artist: Dict or None, the best artist found or None if no artists in results
        """
        artists = result['artists']['items']  # list of dicts

        num_matches = int(result['artists']['total'])
        if num_matches == 0:
            if VERBOSE:
                print("No matches found!")
            return None

        elif num_matches == 1:
            if VERBOSE:
                print ("1 match found: " + artists[0]['name'])
                if artists[0]['name'] == artist_name:
                    print ("Exact match!")
                else:
                    print ("Close enough...")
            return ArtistObject(artists[0], artist_name)

        elif num_matches > 1:
            if VERBOSE:
                print ("%i matches found: " % num_matches + str([a['name'] for a in artists]) )

            # check for exact match
            no_exact_match = True
            for a in artists:
                if a['name'] == artist_name:
                    if VERBOSE:
                        print("Exact match found!")
                    return ArtistObject(a, artist_name)
            # If there is no exact match, the first match is probably best.
            # Consider filtering by popularity or followers here!
            return ArtistObject(artists[0], artist_name)

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

        tracklist.extend(result.get("tracks"))
        if len(tracklist) > N:
            return tracklist[0:N]
        else:
            return tracklist

class ArtistObject():
    def __init__(self, artist={}, searched_name=None, db_model=None):
        # Searched name keeps track of the search term used to find this artist. Name comes from spotify.
        # Saving the searched_name allows us to quickly find the same Spotify Artist, given the same searched_name
        self.name = artist.get("name")
        self.searched_name = searched_name if searched_name is not None else self.name
        self.uri = artist.get("uri")
        self.songs = []
        # plenty of other nice things:  uri, popularity, name, followers.total, genres, images[].url,

        # TODO this seems repetitive and inelegant. How to do it better?
        if db_model is not None:
            self.name = db_model.name
            self.searched_name = db_model.searched_name
            self.uri = db_model.uri
            self.songs = []
            self.add_songs(json.loads(db_model.songs), replace=True)

    def add_songs(self, songs, replace=False):
        if replace:
            self.songs = []
        for song in songs:
            s = SongObject(song)
            self.songs.append(s)

    def get_songs(self, n=NUMBER_OF_SONGS_PER_ARTIST):
        return self.songs[:NUMBER_OF_SONGS_PER_ARTIST]

    def to_dict(self):
        return {
            "name": self.name,
            "uri": self.uri,
        }

    def save_to_db(self):
        if self.uri is None:
            # Empty database record in the case where a match is not found
            # Artist.objects.get_or_create(name=searched_name)
            pass
        else:
            json_songs = json.dumps([s.to_dict() for s in self.songs])
            Artist.objects.get_or_create(searched_name=self.searched_name, name=self.name, uri=self.uri, songs=json_songs)

class SongObject():
    def __init__(self, song):
        self.name = song.get("name")
        self.uri = song.get("uri")

    def to_dict(self):
        return {
            "name": self.name,
            "uri": self.uri,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
