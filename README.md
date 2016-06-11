# musicThisWeek

Generates a Spotify playlist of bands that are playing in your area in the near future.

## Consituent parts

musicThisWeek.py: Main program. Run it without arguments

eventFinder.py: Crawls the internet to return a list of upcoming events in the specified city.

playlistCreator.py: Creates a spotify playlist based on a list of artists.

## Dependencies

Requests (2.9.1)

[Spotipy](https://spotipy.readthedocs.io/en/latest/)

# Instructions

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

3. `sh run.sh` This will source the above file, run the server, and open a browser for you!

4. Follow instructions in the browser

5. Play the playlist by clicking the link or browsing your playists in the Spotify app
 

## Development Status

In early development. Basic working prototype exists. Does not work for generic usernames.

## Disclaimer

This is a personal hobby project, not intended for public use.

Nick Speal 2016. All rights reserved.