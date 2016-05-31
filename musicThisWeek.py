#!/usr/bin/python
'''
Music This Week
Generates a Spotify playlist of bands that are playing in your area in the near future.
Nick Speal 2016
'''

from playlistCreator import PlaylistCreator
import eventFinder

'''
Phase 1: Event Finder
'''

searchArgs = {'location':'San+Francisco',
								'time': 'Next+14+days',
								'nResults': '100'}

EF = eventFinder.EventFinder(searchArgs)

'''
Phase 2: Create Spotify Playlist
'''

pc = PlaylistCreator()
error = pc.login("nickspeal")
if error:
	raise Exception("Login failure")

url = pc.createPlaylist(EF.artists)
print "\n\nSuccessfully Created a playlist! Give it a listen:"
print url
