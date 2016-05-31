'''
Music This Week
'''


from playlistCreator import PlaylistCreator
import eventFinder

'''
Phase 1: Event Finder
'''
# For now hardcoded
#artists = ["Radiohead", "Nick Cave & The Bad Seeds", "The 1975", '314123j312n3k12jn3']

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
