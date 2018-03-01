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

from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import json

from . import backend
from .backend.spotifyHandler import PlaylistCreator
from .backend.spotifyHandler import is_token_valid

class Create(View):
    allowed_methods = ['post', 'options']

    def options(self, request):
        response = HttpResponse()
        response['allow'] = ','.join(self.allowed_methods)
        return response

    def post(self, request):
        """ Search for shows and create playlist then redirect to it"""
        body = json.loads(request.body)
        print("Got POST request with body: ", body)

        if not is_token_valid(body['spotify_token']):
            return HttpResponseForbidden('spotify_token is not valid')

        # Parse request for search arguments
        search_args = body

        # Validate search arguments
        if "location" not in search_args.keys() or search_args["start"] == '' or search_args["end"] == '' or "nResults" not in search_args.keys():
            print("ERROR: Bad search arguments")
            print(search_args)
            resp = HttpResponseBadRequest("Bad Search Arguments")
            return resp

        # Load PlaylistCreator
        pc = PlaylistCreator()
        pc.complete_login(body['spotify_token'])

        # Main heavy lifting happens in the background
        # TODO do this asyncronously! Create and return and empyty playlist and then go from there!
        (url, error) = backend.execute(pc, search_args)

        if error is not None:
            print("Error in backend execute: ", error)
            resp = HttpResponseBadRequest(error)
            return resp

        r = {
            'playlist': url
        }

        return JsonResponse(r)
