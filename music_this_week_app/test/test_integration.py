#!/usr/bin/python
'''
Music This Week
Generates a Spotify playlist of bands that are playing in your area in the near future.
Nick Speal 2016
'''

from music_this_week_app.backend.playlistCreator import PlaylistCreator
import music_this_week_app.backend.eventFinder as eventFinder


#Instantiate
pc = PlaylistCreator()

pc.cli_login(username="nickspeal")

search_args = {'location': 'San+Francisco',
              'time': 'next+7+days',
              'nResults': '99'}

# Search for list of upcoming artists
EF = eventFinder.EventFinder(search_args)

# Create a Spotify playlist with those artists
url = pc.createPlaylist(EF.unfilteredArtists)

print "\n\nSuccessfully Created a playlist! Give it a listen:"
print url