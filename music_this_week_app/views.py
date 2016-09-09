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
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError
import backend
from backend.spotifyHandler import PlaylistCreator


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
    #get user ip address to find user location 
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    #handle invalid IP or ip == 127.0.0.1 because running locally 
    try:
        g = GeoIP2()
        location = g.city(ip)
    except AddressNotFoundError:
        location = {'city' : "San Francisco"}
    # Fetch user data
    pc = request.session.get('pc')
    if pc is None:
        print("ERROR: setup called without pc session. Redirecting home.")
        return HttpResponseRedirect('/')

    context = dict(pc.user_info, **{'location' : location['city']}) 
    return render(request, 'music_this_week/setup.html', context)

def search(request):
    """ Search for shows and create playlist then redirect to it"""
    # Parse request for search arguments
    search_args = dict(request.GET.items())
    print(search_args)
    #Validate search arguments
    keys = search_args.keys()
    if ("location" not in keys and ("hidden_lat" not in keys or "hidden_lon" not in keys)) or "date" not in keys or "nResults" not in keys:
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

    return HttpResponseRedirect(url)
