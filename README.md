# musicThisWeek

Generates a Spotify playlist of bands that are playing in your area in the near future.

## Consituent parts

Django web app: Site is called music_this_week, and the app is called music_this_week_app.

eventFinder.py: Crawls the internet to return a list of upcoming events in the specified city.

playlistCreator.py: Creates a spotify playlist based on a list of artists.

## Development Status

In early development. Basic working prototype exists. Does not work for generic users.

## Disclaimer

This is a personal hobby project, not intended for public use.

Nick Speal 2016. All rights reserved.


# Setup

## Dependencies

Requests (2.9.1)

[Spotipy](https://spotipy.readthedocs.io/en/latest/)

Django (1.9.7)

## Instructions

1. Install dependencies

	~~~~
	pip install requests

	pip install spotipy

	pip install Django
	~~~~

2. create a config file called spotipyCreds.sh:

	~~~~
	export SPOTIPY_CLIENT_ID='ask me for the client ID'

	export SPOTIPY_CLIENT_SECRET='ask me for the secret'

	export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'

	export DJANGO_SECRET_KEY='ask me'

    export EVENTFUL_KEY='ask me'
	~~~~

3. `sh run.sh` This will source the above file, start the server, and open a browser for you!

4. Follow instructions in the browser

5. Play the playlist in the browser or find it automatically ready in the Spotify app
 

# Documentation

## How Spotify Authentication works

* Leans heavily on the [Spotipy](https://spotipy.readthedocs.io/en/latest/) client library
* `playlistCreator.init_login()` is called with credentials stored in environment vars.
* It returns an object saved as sp_oauth.
* We call `its get_authorize_url()` method, which returns a URL we can redirect the browser to in order to go through Spotify's login flow.
* If no cookies are saved, spotify asks the user to log in. If there is a cookie, this step is skipped
* Spotify redirects the browser to our /callback endpoint, sending a code along with it.
* We exchange this code for an access token and a refresh_token
* We use the access token to call spotipy.Spotify() and get a handle for all future Spotify operations.
* There is no explicit way to log out, but you can force the user to log in again (with the option to change accounts) by appending `&show_dialog=True` to the Authorization endpoint(Not supported by Spotipy).
* More details on [Spotify's website](https://developer.spotify.com/web-api/authorization-guide/)

## User Flows

1. New user goes to the website, logs in for the first time, specifies search parameters, creates a playlist.
2. Returning: User returns to the website, is automatically logged in and search params are loaded, creates a playlist _(Not done yet)_
3. AutoRun: For each user, saved searches are repeated and playlists are updated periodically _(Not done yet)_


