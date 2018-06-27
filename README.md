# Music This Week

Music This Week is a music discovery service that generates a Spotify playlist of bands that are playing near you in the near future.

## Constituent parts

Django web app: Site is called music_this_week, and the app is called music_this_week_app.

eventFinder.py: Crawls the internet to return a list of upcoming events in the specified city.

playlistCreator.py: Creates a spotify playlist based on a list of artists.

## Development Status

In early development. Basic working prototype exists. Does not work for generic users.

## Disclaimer

This is a personal hobby project, not intended for public use.

Nick Speal 2016. All rights reserved.



## Setup Instructions

1. Create a virtual environment for your project.

    To keep your pip installation clean, we recommend using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).

    ~~~~
    $ mkvirtualenv mtw
    ~~~~

    Anytime you want to run this project, run:

    ~~~~
    $ workon mtw
    ~~~~

1. Install dependencies in your virtualenv from the root of the repo.

    ~~~~
    $ pip install -r requirements.txt
    ~~~~

1. Also install Redis:

  ~~~~
  $ brew install redis
  ~~~~

1. Create a config file called spotipyCreds.sh under a (gitignored) directory under the root called '_private':

    ~~~~
    $ echo "
    export SPOTIPY_CLIENT_ID='Create a new app at developer.spotify.com to get this'
    export SPOTIPY_CLIENT_SECRET='Create a new app at developer.spotify.com to get this'
    export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
    export DJANGO_SECRET_KEY='make one up'
    export EVENTFUL_KEY='Request an application key from https://api.eventful.com/keys'
    " > _private/spotipyCreds.sh
    ~~~~

## Running Instructions

1. cd into the root of the repo

1. Start the redis server: `redis-server`

1. In a new terminal window, open the project's virtualenv: `workon mtw`

1. Load the private environment variables: `source _private/spotipyCreds.sh`

1. Run the appropriate workers: `python manage.py runworker search song events`

1. In a new terminal window, open the project's virtualenv: `workon mtw`

1. Run the backend: `sh run.sh` (Prereq: Make sure you already ran the setup instructions at some previous point.)

1. In a new terminal window, cd into the musicthisweek-client directory with the frontend application and then run it, (probably `npm start`);

1. Open the frontend application in the browser and follow the instructions


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

For CLI Login:
* We use `spotifyHander.PlaylistCreator.cli_login()` for a UI-free login
* This uses a different spotipy method than the main flow.
* We call `util.prompt_for_user_token()` with a `username` argument. Spotipy searches for a cached token file in the root directory called `.cache-username`
* If that cache exists, we already have a token to use. If it doesn't, then we need to go through some back and forth in the browerser/cli.
* `util.prompt_for_user_token()` always calls `oauth2.SpotifyOAuth` with the optional `cache_path` argument, so the cache file is always created if it didn't exist.
* The cache file is not used for the main flow because the user's username is not known before they attempt to log in so we depend on Spotify's cookies, rather than a local cache.

## User Flows

1. New user goes to the website, logs in for the first time, specifies search parameters, creates a playlist.
2. Returning: User returns to the website, is automatically logged in and search params are loaded, creates a playlist _(Not done yet)_
3. AutoRun: For each user, saved searches are repeated and playlists are updated periodically _(Not done yet)_
