#!/usr/bin/python
"""
Main logic for Music This Week.

Home renders homepage
User clicks Login, which redirects to Spotify Auth
Spotify redirects to callback, which completes the login by getting an access token and then redirects to /setup
In /setup, the user specifies serach args then presses the search button, which calls /search
/search calls eventFinder with the search_args and then calls create_playlist with the list of artists
After a playlist is created, it redirects to the playlist URL
"""


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from backend.spotifyHandler import PlaylistCreator
import backend.master

master = backend.master.Master() # master backend object for doing all the heavy lifting

def home(request):
    context = {}
    return render(request, 'music_this_week/home.html', context)


def login(request):
    """Redirects user to Spotify Login page"""

    # Instantiate a PlaylistCreator object for this user.
    pc = PlaylistCreator()

    # Ask Spotify for a login URL to send users to
    auth_url = pc.init_login()
    print("Talking to Spotify. Redirecting for authorization")

    # Save PlaylistCreator instance
    # TODO SECURITY ISSUE: Pickle Session Serialization is unsafe
    request.session['pc'] = pc

    # Set session to expire when the browser closes
    request.session.set_expiry(0)

    return HttpResponseRedirect(auth_url)


def callback(request):
    """Response from Spotify Authentication comes to this endpoint with a code to continue"""
    # Load PlaylistCreator
    pc = request.session['pc']

    # Parse out code from Spotify's request
    code = request.GET['code']

    # Log in to Spotify with the code
    pc.login(code)

    # Save PlaylistCreator instance
    request.session['pc'] = pc

    return HttpResponseRedirect('/setup')


def setup(request):
    """Displays search args and a search button, which links to /search"""
    context = {}
    return render(request, 'music_this_week/setup.html', context)

def search(request):
    """ Search for shows and create playlist then redirect to it"""

    # In the future, these search args will arrive with the HTTP request. Hardcoded for now
    searchArgs = {'location':'San+Francisco',
                  'time': 'next+7+days',
                  'nResults': '4'}

    # Load PlaylistCreator
    pc = request.session['pc']

    # Main heavy lifting happens in the background
    url = master.execute(pc, searchArgs)

    # Save PlaylistCreator instance, just in case
    request.session['pc'] = pc

    return HttpResponseRedirect(url)