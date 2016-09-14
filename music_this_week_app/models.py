from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Artist(models.Model):
    name = models.CharField(max_length = 50, primary_key = True)
    #it looks like spotify id is always 22 chars but add a few more to be safe
    spotify_uri = models.CharField(max_length = 28, null = True)
    top_tracks = models.CharField(max_length = 10*28, null = True)

    def __str(self):
        return self.spotify_uri
