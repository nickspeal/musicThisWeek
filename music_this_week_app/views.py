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
# from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect

from backend.playlistCreator import PlaylistCreator
import backend.eventFinder as eventFinder

pc = PlaylistCreator()


def home(request):
    context = {}
    return render(request, 'music_this_week/home.html', context)


def login(request):
    """Redirects user to Spotify Login page"""
    auth_url = pc.init_login()
    print "Talking to Spotify. Redirecting for authorization"
    return HttpResponseRedirect(auth_url)


def callback(request):
    """Response from Spotify Authentication comes to this endpoint with a code to continue"""
    print "callback from spotify"
    code = request.GET['code']
    pc.login(code)
    return HttpResponseRedirect('/setup')


def setup(request):
    """Displays search args and a search button, which links to /search"""
    context = {}
    return render(request, 'music_this_week/setup.html', context)

def search(request):
    searchArgs = {'location':'San+Francisco',
                  'time': 'next+7+days',
                  'nResults': '4'}

    # Search for list of upcoming artists
    EF = eventFinder.EventFinder(searchArgs)

    # Create a Spotify playlist with those artists
    url = pc.createPlaylist(EF.unfilteredArtists)

    print "\n\nSuccessfully Created a playlist! Give it a listen:"
    print url

    return HttpResponseRedirect(url)