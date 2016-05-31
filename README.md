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

2. Export the following environment variables:

	~~~~
	export SPOTIPY_CLIENT_ID='ask me for the client secret'

	export SPOTIPY_CLIENT_SECRET='ask me for the secret'

	export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
	~~~~

3. `python musicThisWeek.py`

4. follow instructions
 

## Development Status

In early development. Building up the components one block at a time.

## Disclaimer

This is a personal hobby project, not intended for public use.

Nick Speal 2016. All rights reserved.