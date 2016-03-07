# musicThisWeek

Generates a Spotify playlist of bands that are playing in your area in the near future.

## Consituent parts

eventFinder.py: Crawls the internet to return a list of upcoming events in the specified city.

generatePlaylist.py: Creates a spotify playlist based on a list of artists. (Not done yet)

## Dependencies

requests (2.9.1)

Node.js

A whole bunch of dependencies in packages.json. Type `npm install` to install them.

# Instructions

1. Install dependencies

2. run `python eventFinder.py` to get a list of local events

3. run `node app.js` to run the server. Keep it going

4. run `python generatePlaylist.py` 

5. A web browser will pop up. Log into Spotify and then close the browser.

6. The python program will attempt to create a spotify playlist (But fail as of now, due to auth issues)

## Status

In early development. Building up the components one block at a time.

## Disclaimer

This is a personal hobby project, not intended for public use.

Nick Speal 2016. All rights reserved.