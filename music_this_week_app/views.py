#!/usr/bin/python
"""
Main logic for Music This Week.

Home renders homepage
User clicks Login, which redirects to Spotify Auth
Spotify redirects to callback, which completes the login by getting an access token and then redirects to /setup
In /setup, the user specifies search args then presses the search button, which calls /search
/search calls eventFinder with the search_args and then calls create_playlist with the list of artists
After a playlist is created, it redirects to the playlist URL
"""


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from . import backend
from .backend.spotifyHandler import PlaylistCreator


def home(request):
    """Show the user a home page with a button to get started"""
    context = {}
    return render(request, 'music_this_week/home.html', context)


def login(request):
    """Redirects user to Spotify Login page"""

    # Instantiate a PlaylistCreator object for this user.
    pc = PlaylistCreator()

    # Ask Spotify for a login URL to send users to
    auth_url = pc.init_login()


    retry = request.GET.get('retry')
    print("Talking to Spotify. Redirecting for authorization with retry = %s" % retry)
    if retry == 'true':
        auth_url = auth_url + '&show_dialog=True'

    # Save PlaylistCreator instance
    # TODO SECURITY ISSUE: Pickle Session Serialization is unsafe
    request.session['pc'] = pc

    # Set session to expire when the browser closes
    request.session.set_expiry(0)

    return HttpResponseRedirect(auth_url)


def callback(request):
    """Response from Spotify Authentication comes to this endpoint with a code to continue"""
    # Load PlaylistCreator
    pc = request.session.get('pc')
    if pc is None:
        print("ERROR: callback called without pc session. Redirecting home.")
        return HttpResponseRedirect('/')

    # Check for login error
    # for example, if the user hits cancel, we get "error=access_denied"
    error_message = request.GET.get('error')
    if error_message is not None:
        print("ERROR: Could not authenticate with Spotify")
        print(error_message)
        return HttpResponseRedirect('/')

    # Parse out code from Spotify's request
    code = request.GET.get('code')

    # Log in to Spotify with the code
    pc.login(code)

    # Save PlaylistCreator instance
    request.session['pc'] = pc

    return HttpResponseRedirect('/setup')


def setup(request):
    """Displays search args and a search button, which links to /search"""

    # Fetch user data
    pc = request.session.get('pc')
    if pc is None:
        print("ERROR: setup called without pc session. Redirecting home.")
        return HttpResponseRedirect('/')

    location = request.session.get('location')
    if location is None:
        location = 'San Francisco'
    context = dict(pc.user_info, **{'location': location} )
    return render(request, 'music_this_week/setup.html', context)

def search(request):
    """ Search for shows and create playlist then redirect to it"""
    # Parse request for search arguments
    search_args = dict(request.GET.items())

    # Validate search arguments
    if "location" not in search_args.keys() or search_args["start"] == '' or search_args["end"] == '' or "nResults" not in search_args.keys():
        print("ERROR: Bad search arguments")
        print(search_args)
        resp = HttpResponse("Bad Search Arguments")
        resp.status_code = 400
        return resp

    # Load PlaylistCreator
    pc = request.session.get('pc')
    if pc is None:
        print("ERROR: search called without pc session. Redirecting home.")
        return HttpResponseRedirect('/')

    # Main heavy lifting happens in the background
    (url, error) = backend.execute(pc, search_args)

    # Save PlaylistCreator instance, just in case
    request.session['pc'] = pc

    if error is not None:
        resp = HttpResponse(error)
        resp.status_code = 400
        return resp

    # Save user's search location as a cookie for next time
    request.session['location'] = search_args.get('location')

    return HttpResponseRedirect(url)
