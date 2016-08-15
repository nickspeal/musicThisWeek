from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Artist(models.Model):
    name = models.CharField(max_length=50, primary_key = True)
    spotify_uri = models.CharField(max_length= 100)

    def __str__(self):
        return self.spotify_uri
