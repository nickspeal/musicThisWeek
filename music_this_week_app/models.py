from __future__ import unicode_literals

from django.db import models

class Artist(models.Model):
    searched_name = models.CharField(max_length = 50, primary_key = True)
    name = models.CharField(max_length = 50, null = True)
    uri = models.CharField(max_length = 100, null = True)
    songs = models.CharField(max_length=1000, null = True) # this max_length could come back to bite me... JSON formatted [{"name": "blah", "uri":"blah"}, ...]

    def __str(self):
        return self.spotify_uri
