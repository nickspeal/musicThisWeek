'''
Music This Week
'''

import sys
import spotipy
import spotipy.util as util
import pprint
from random import shuffle


def findTopTracks(artist, N=10):
	'''
	Given a plaintext artist name, return a list of the top N tracks (default 10)
	Returns nothing if no results.
	'''
	
	# Step1: Given an artist name, find a single artistURI
	result = sp.search(q='artist:' + artist, type='artist')
	artists = result['artists']['items'] #list of dicts
	print "\n\n Searching for artist: " + artist
	numMatches = int(result['artists']['total'])
	print "%i artists found." %numMatches
	if numMatches == 0:
		return []
	elif numMatches == 1:
		artistURI = artists[0]['uri']
		print "Spotify Artist Name: " + artists[0]['name']
	elif numMatches > 1:
		#Assume there is no exact match, so the first match is probably best.
		artistURI = artists[0]['uri']
		print "First result: " + artists[0]['name']
		#check for exact match
		for item in artists:
			if item['name'] == artist:
				print "Exact match found!"
				artistURI = item['uri']
	else:
		raise Exception('unexpected number of matches (%i) for artist %s' %(numMatches,artist))

	#Step 2: Given an artistURI, find a list of tracks
	tracklist = []
	result = sp.artist_top_tracks(artistURI)
	for track in result['tracks']:
		tracklist.append(track['uri'])
	return tracklist




'''
Phase 1: Event Finder
'''
# For now hardcoded
artists = ["Radiohead", "Nick Cave & The Bad Seeds", "The 1975"]


'''
Phase 2: Create Spotify Playlist
'''



''' Prompt user to log in '''

username = "nickspeal"

print "Please Log into Spotify"
print "Username: " + username

scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope)
if not token:
	print "Can't get token for", username
	sys.exit()
else:
	sp = spotipy.Spotify(auth=token)
	sp.trace = False # No idea what this does...


'''Create New Playlist'''
# Check if a musicThisWeek playlist exists
# if not, create one, and get playlist ID
# if yes, get playlist ID

# replace tracks in playlist

playlist_name = "musicThisWeek"
playlistExists = False
playlistURI = None

playlists = sp.user_playlists(username)
for playlist in playlists['items']:
	if playlist['name'] == playlist_name:
		playlistExists = True
		playlistURI = playlist['uri']

if playlistExists:
	print "Matching playlist already exists. It will be replaced."
else:
	print "Matching playlist does not exist. It will be created."
	playlist = sp.user_playlist_create(username, playlist_name)
	playlistURI = playlist['uri']

print "Ready to add content to playlist with URI: " + playlistURI

# Identify songs for the playlist
track_ids = []

for artist in artists:
	track_ids = track_ids + findTopTracks(artist)

print "Found %i tracks. Ready to add to playlist" %len(track_ids)


# Create playlist from songIDs
shuffle(track_ids)
results = sp.user_playlist_replace_tracks(username, playlistURI, track_ids)
if results is not None:
	print "ERROR adding content to playlist"
	pprint.pprint(results)