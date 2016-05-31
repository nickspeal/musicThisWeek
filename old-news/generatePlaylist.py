#! /usr/bin/python
'''Generates a Spotify playlist based on a list of artists'''

import requests
import webbrowser
import subprocess as sp #unused?
import time


print "Welcome To the Spotify Playlist Generator! \n"
newUser = True
# newUser = False

# Log in!
if newUser:
	print "Please log in and then a playlist will be created in your account"	

	browser = webbrowser.get('safari') #chrome is failing for me for some reason.
	browser.open_new_tab('localhost:8888/login')
	
while True:
		print "sending check check_credentials request"
		resp = requests.get('http://localhost:8888/check_credentials')
		# app will continuously send back status code 204 messages (no content) until it has something to send.
		if resp.status_code == 204:
			print "Received no content. Waiting for the user to log in. Sleeping."
			time.sleep(5) #seconds
		elif resp.status_code == 200:
			print "Got access token."
			break
		else:
			raise Exception('Unexpected Status Code: %i' %resp.status_code)

#requests.get('http://localhost:8888/kill') #shut down the server

#print resp.json()
#ID = resp.json()['user_id'] #TODO
ID = 'nickspeal'
token = resp.json()['access_token']


# Create Spotify Playlist

resp2 = requests.post('https://api.spotify.com/v1/users/%s/playlists' %ID,
											headers= {'Authorization': token},
											data = {'name':'SF_Playlist', 'public':'false'})
if resp2.status_code is not 200:
	print resp2.status_code
	print resp2.reason
else:
	print "success"
print resp2.content



# TODO

#Playlist generation fails with:

# 400
# Bad Request
# {
#   "error": {
#     "status": 400,
#     "message": "Only valid bearer authentication supported"
#   }
# }












# Try to run server in the background. Not sure how to do it.
# sp.Popen('node /Users/Nick/Coding/musicThisWeek/scrap/web-api-auth-examples/authorization_code/app.js')
# p.wait()







# import urllib

# scope = 'user-read-private user-read-email'
# client_id = '338af3083e4e4069960c77b6978cb7a5'
# client_secret = '9beb594d85ce466a9bf208de1f89aad3'
# redirect_uri = 'http://localhost:8888/callback' # UNUSED?


# # Authorize with Spotify
# args = {'response_type': 'code',
# 				'client_id': client_id,
# 				'scope': scope}
# 				#missing redirect_uri: redirect_uri,
# 				# missing 'state': state

# URL = 'https://accounts.spotify.com/authorize?' + urllib.urlencode(args)
# print "hitting endpoint: %s" %URL

# res.redirect('https://accounts.spotify.com/authorize?' +
#   querystring.stringify({
#     response_type: 'code',
#     client_id: client_id,
#     scope: scope,
    
#     state: state
#   }));


# res = requests.post()