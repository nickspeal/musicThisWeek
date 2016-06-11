#!/usr/bin/python
"""
handles all interactions with Spotify
musicThisWeek
Nick Speal 2016
"""

import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2 #for login
from random import shuffle


class Playlist(object):
    def __init__(self):
        self.tracknames = []
        self.track_ids = []


class PlaylistCreator(object):
    def __init__(self):
        self.sp_oauth = None # Created in init_login
        self.username = None # Created in init_login or cli_login

    def createPlaylist(self, artists, name = "musicThisWeek"):
        """
        Creates a playlist in the USERNAME's account with content from the list of artists passed as an argument
        Creates a new playlist if one doesn't already exist, otherwise it overwrites the existing one
        """
        playlistURL = self.getSpotifyPlaylist(name)


        # Filter the list of artists
        artistURIs = [self.filterArtist(a) for a in artists]
        artistURIs = [a for a in artistURIs if a is not None]

        print "\n%i of the %i artists were found on Spotify." %(len(artistURIs), len(artists))
        # Identify songs for the playlist; list of track URIs
        self.tracks = []
        for a in artistURIs:
            self.tracks = self.tracks + self.findTopTracks(a, N=2)

        # Randomize playlist order
        shuffle(self.tracks)

        tracklist = self.tracks[0:99] #quick hack to get around 100 song limit for now.

        print "Creating playlist of length: %i" %len(tracklist)
        # Add trackIDs to playlist
        self.sp.user_playlist_replace_tracks(self.username, playlistURL, tracklist)
        return playlistURL


    def init_login(self,):
        self.username = "nickspeal" # hardcoded - TODO read this after user logs in.
        # Don't check this stuff in!!
        client_id='338af3083e4e4069960c77b6978cb7a5'
        client_secret='9beb594d85ce466a9bf208de1f89aad3'
        redirect_uri='http://localhost:8888/callback'
        scope = 'playlist-modify-public'

        self.sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=".cache-" + self.username)
        return self.sp_oauth.get_authorize_url()

    def login(self, code):
        token = self.sp_oauth.get_access_token(code)
        if token:
            self.sp = spotipy.Spotify(auth=token['access_token'])
            self.sp.trace = False # No idea what this does...
        else:
            raise Exception("ERROR: Can't get a token for ", self.username)

    def cli_login(self, username):
        """
        Helper method for integration testing.
        init_login() and login() depend on a browser UI. This does something similar but works from the cli
        :return:
        """
        self.username = username
        scope = 'playlist-modify-public'
        token = util.prompt_for_user_token(self.username, scope)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.sp.trace = False  # No idea what this does...
        else:
            raise Exception("Can't get token from Spotify")

    def filterArtist(self, artist):
        """
        Given a plaintext artist name, return a Spotify Artist URI
        Returns None if no results found
        """

        print "\nSearching for artist: " + artist
        result = self.sp.search(q='artist:' + artist, type='artist')
        artists = result['artists']['items'] #list of dicts

        numMatches = int(result['artists']['total'])
        if numMatches == 0:
            print "No matches found!"
            return None

        elif numMatches == 1:
            print "1 match found: " + artists[0]['name']
            if artists[0]['name'] == artist:
                print "Exact match!"
            else:
                    print "Close enough..."
            return artists[0]['uri']

        elif numMatches > 1:
            print "%i matches found: "%numMatches + str([a['name'] for a in artists])
            #check for exact match
            for a in artists:
                if a['name'] == artist:
                    print "Exact match found!"
                    return a['uri']
            #If there is no exact match, the first match is probably best.
            return artists[0]['uri']

        else:
            raise Exception('unexpected number of matches (%i) for artist %s' %(numMatches,artist))

    def findTopTracks(self, artist, N=10):
        """
        Given a unique artist identifier (URI), return a list of N top tracks
        """
        tracklist = []
        result = self.sp.artist_top_tracks(artist)
        for track in result['tracks']:
            tracklist.append(track['uri'])
        if len(tracklist) > N:
            return tracklist[0:N-1]
        else:
            return tracklist

    def getSpotifyPlaylist(self, title):
        """
        Returns a playlist URL matching a user's playlist with a specified name.
        Creates the playlist if it doesn't exist yet.
        """
        # Check if playlist already exists
        users_playlists = self.sp.user_playlists(self.username)
        for playlist in users_playlists['items']:
            if playlist['name'] == title:
                return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

        # Create new playlist if needed
        playlist = sp.user_playlist_create(self.username, title)
        return playlist['external_urls']['spotify'] #Return URL not URI so that it can be passed to the user. playlist['uri'] also works.

    def printDiagnostics(self):
        """If requested, display debug info about the playlist generation process"""
        print "Number of tracks found: %i" %len(self.tracks)