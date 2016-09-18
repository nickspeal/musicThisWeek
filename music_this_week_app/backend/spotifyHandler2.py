#!/usr/bin/python
"""
handles all interactions with Spotify
musicThisWeek
Nick Speal 2016
"""

import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2 # for login
from random import shuffle
from music_this_week_app.models import Artist
import os

VERBOSE = False

class SpotifySearcher(object):
    """Handles unauthenticated Spotify requests like searching for artists and songs"""

    def __init__(self):
        # Init unauthorized Spotify handle
        self.sp = spotipy.Spotify()  # This should be the only instance attribute, to maintain statelessness
        #a list of the artist models retrieved from db
        self.db_artists = []
        # a list of the new artist models
        self.new_artists = []


    def fill_artist_lists(self, unfiltered_artist_names):
        """
        Turn a list of potential artist names into a list of Spotify artist URIs
        Filter out artists that cannot be found from the list.

        :param unfiltered_artist_names: list of strings of artist names
        :return artistURIs: list of strings of verified Spotify artist identifiers
        """

        for artist_name in unfiltered_artist_names:
            self.add_artist_to_lists(artist_name)
        for artist in self.new_artists:
            #keep this order, because need uri to find tracks
            self.update_artist_uri(artist)
            self.update_artist_top_tracks(artist)
            artist.save()
        self.assemble_track_list(self.new_artists + self.db_artists)
        
              
         
    def add_artist_to_lists(self, artist_name):
        """ 
        looks in the database for an artist matching this name and adds it to 
        db_artists if it exists. If not it instantiates an artist and adds it to
        new_artists 

        :param artist_name: string
        """
        try:
            artist_entry = Artist.objects.get(name = artist_name)
            self.db_artists.append(artist_entry)
        except Artist.DoesNotExist:
            artist_entry = Artist(name = artist_name)
            self.new_artists.append(artist_entry)
              
            
    def update_artist_top_tracks(self, artist):
        """
        takes an artist and updates their top_tracks attribute with their top tracks ffound on spotify
 
        :param artist: an Artist object to be updated
        :return None:
        """
       tracks = self.find_artist_top_tracks(artist.spotify_uri)
       #store uris as a string
       #TODO trim spotify:track: from front
       artist.top_tracks = ",".join(tracks) 
         

    def update_artist_uri(self, artist):
        """
        Takes an Artist object and searches spotify to update the artist's spotify_uri 
       sets spotify_uri to None if no matching artist.name found on spotify 

        :param artist: models.Artist 
        :return None: 
        """
        

        search_result = self.search_spotify(artist.name)

        # If there were any errors searching Spotify, don't continue
        if search_result is None:
            artist_uri = None
        else:
            artist_uri = self.filter_spotify_result(search_result, artist.name)

       #update artist spotify uri with None or the uri from searching
       #TODO: trim spotify:artist: from front
       artist.spotify_uri = artists_uri

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

    def save_new_artist(self, artist_name, artist_uri, artist_tracks):
        """
        saves artist name/uri pairs to DB
        :param artist_name: String
        :param artist_uri: String
        :param artist_tracks: list
        :return None:
        """
        if artist_uri is not None:
            #all artist uris begin with spotify:artist: . therefore save space in DB by omitting first 15 char        
            artist_uri = artist_uri[15:]
        artist_tracks = ','.join(artist_tracks)
        artist, created = Artist.objects.get_or_create( name=artist_name,)
        if created:
            artist.spotify_uri = artist_uri
            artist.top_tracks = artist_tracks
            artist.save()

    def get_number_uris_found(self):
        """
        calculates the number of artists in new_artists and db_artists with a spotify URI
        
        :return int:
        """
        total_artists = self.new_artists + self.db_artists
        return len([artist in total_artists if artist.spotify_uri is not None] )

    def assemble_track_list(self, N=99, order="shuffled"):
        """
        Come up with a list of songs by a given list of artists

        :param N: Desired length of the list
        :param order: Desired order of the list. Can be "shuffled". Other options may be added later
        :return tracklist: List of spotify track URIs, to create playlist later.
        """

        # Calculate number of tracks per artist. Round up to nearest int w/ int division then trim list later.
        number_of_tracks_per_artist = N // self.get_number_uris_found() + 1
        if number_of_tracks_per_artist > 10:
            print("Number of tracks per artist, %i, cannot be greater than 10." %number_of_tracks_per_artist)

        # Identify songs for the playlist; list of track URIs
        tracks = []
        total_artists = self.new_artists + self.db_artists
        for artist in total_artists:
            artist_tracks = artist.top_tracks.split(',')
            num_playlist_tracks = max(number_of_tracks_per_artist, len(artist_tracks) )
            tracks += artist_tracks[:num_playlist_tracks]

        if order == "shuffled":
            # Randomize playlist order
            shuffle(tracks)
            print("Prior to trimming, the playlist is %i songs long" %len(tracks))
            tracklist = tracks[:N]
        else:
            raise Exception("Invalid song list order specified")

        return tracklist

    def find_artist_top_tracks(self, artist_uri, N=10):
        """
        Return top N tracks by one artist

        :param artist_uri: String the artist URI
        :param N: int maximum number of tracks to return. Cannot be greater than 10
        :return: list of track URIs
        """
        tracklist = []
        if artist_uri == None:
            return tracklist
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

class PlaylistCreator(object):
    def __init__(self):
        self.sp_oauth = None # Created in init_login
        self.username = None # Created in get_user_info
        self.user_info = {} # Created in get_user_info
        self.sp = None # created in login or cli_login

    def init_login(self):
        client_id=os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        scope = 'playlist-modify-public'
        self.sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
        return self.sp_oauth.get_authorize_url()

    def login(self, code):
        token = self.sp_oauth.get_access_token(code)
        self.complete_login(token['access_token'])

    def cli_login(self, username):
        """
        Helper method for integration testing.
        init_login() and login() depend on a browser UI. This does something similar but works from the cli
        :param username: name that a cached token would be saved under, in the form of .cache-username
        :return:
        """

        scope = 'playlist-modify-public'

        # If a file called .cache-username exists, the cached token is used without having to talk to Spotify
        token = util.prompt_for_user_token(username, scope)
        self.complete_login(token)

    def complete_login(self, token):
        """Common code for both cli_login() and login()"""
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.sp.trace = False  # No idea what this does...
            self.get_user_info()
        else:
            raise Exception("ERROR: Can't get a token from Spotify")


    def is_logged_in(self):
        """Check if a Spotify handle exists"""
        if self.sp:
            return True
        else:
            return False

    def get_user_info(self):
        """
        Immediately after login, save some information about the user

        self.username is used in other methods
        self.user_info is used in the /setup page to show profile info to the user
        """
        # sp.me() returns the following info:
        #
        # product
        # display_name
        # external_urls
        # country
        # uri
        # id
        # href
        # followers
        # images (list of dicts with these keys)
        #     url
        #     width
        #     height
        # type
        # email

        user = self.sp.me()
        self.username = user['id']
        try:
            photo_url = user['images'][0]['url']
        except IndexError:
            # If user has no photo, use Spotify Logo
            photo_url = 'https://lh3.googleusercontent.com/UrY7BAZ-XfXGpfkeWg0zCCeo-7ras4DCoRalC_WXXWTK9q5b0Iw7B0YQMsVxZaNB7DM=w300'
        self.user_info = {"username": self.username,
                          "display_name": user['display_name'],
                          "profile": user['external_urls']['spotify'],
                          "profile_photo": photo_url,
                          "email": user.get('email')
                          }

    def get_spotify_playlist(self, title):
        """
        Returns a playlist URL matching a user's playlist with a specified name.
        Creates the playlist if it doesn't exist yet.

        :param title: Playlist name
        :return: Playlist URL (Not URI - we'll need to redirect to it)
        """

        # Check if playlist already exists
        users_playlists = self.sp.user_playlists(self.username)
        for playlist in users_playlists['items']:
            if playlist['name'] == title:
                return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

        # Create new playlist if needed
        playlist = self.sp.user_playlist_create(self.username, title)
        return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

    def erase(self, playlist):
        """
        Replace an empty playlist

        :param playlist: Spotify Playlist URL (or URI - whatever)
        :return:
        """
        self.sp.user_playlist_replace_tracks(self.username, playlist, [])

    def add(self, playlist, song_list):
        """
        Adds a list of track IDs to a specified playlist ID

        :param playlist: Playlist URL (or URI, whatever)
        :param song_list: list of song URIs
        :return:
        """
        # Add songs to playlist 99 tracks at a time (Spotify limit)
        i=0
        while(i<len(song_list)):
            self.sp.user_playlist_add_tracks(self.username, playlist, song_list[i:i+99])
            i += 99
