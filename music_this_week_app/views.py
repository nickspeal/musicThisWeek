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

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .SpotifyHandler.SpotifyUser import SpotifyUser

class Test(View):
    allowed_methods = ['get']

    def options(self, request):
        response = HttpResponse()
        response['allow'] = ','.join(self.allowed_methods)
        return response

    def get(self, request):
        return HttpResponse('Hello World', status=200)

class Create(View):
    allowed_methods = ['post', 'options']

    def _get_token(self, request):
        try:
            header = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            print('Error: HTTP Authorization header is missing. Headers included:', request.META)
            return None

        try:
            token = header.split('Bearer: ')[1]
        except IndexError:
            print('Error: Authorization Header must contain the string "Bearer: "')
            return None
        return token

    def _valid_search_args(self, search_args):
        if "location" not in search_args.keys():
            print("Error: Location missing from search arguments", search_args)
            return False
        if "nResults" not in search_args.keys():
            print("Error: nResults missing from search arguments", search_args)
            return False
        if search_args["start"] == '':
            print("Error: Start Date missing from search arguments", search_args)
            return False
        if search_args["end"] == '':
            print("Error: End Date missing from search arguments", search_args)
            return False
        return True

    def options(self, request):
        response = HttpResponse()
        response['allow'] = ','.join(self.allowed_methods)
        return response

    def post(self, request):
        """ """
        body = json.loads(request.body)
        print("Got POST request with body: ", body)

        # VALIDATE TOKEN
        token = self._get_token(request)
        spotify_user = SpotifyUser(token)
        if not spotify_user.is_token_valid():
            return HttpResponseForbidden('Spotify token is not valid')

        # VALIDATE SEARCH ARGS
        # Parse request for search arguments
        search_args = body
        if not self._valid_search_args(search_args):
            return HttpResponseBadRequest("Bad Search Arguments")

        # Get Playlist ID
        playlistURL = spotify_user.get_spotify_playlist(erase=True)

        # Asynchronously populate playlist
        async_to_sync(get_channel_layer().send)(
            "search",
            {
                "type": "start_search",
                "playlist": playlistURL,
                "search_args": search_args,
                "token": token,
            },
        )

        return JsonResponse({ "playlist": playlistURL })
