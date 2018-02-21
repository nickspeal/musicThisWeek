from django.test import TestCase



import music_this_week_app.backend.spotifyHandler as spotifyHandler
from music_this_week_app.models import Artist

class test_filter_list_of_artists(TestCase):
    """
    Test how accurately we filter a list of artist names
    """

    def setUp(self):
        self.searcher = spotifyHandler.SpotifySearcher()

    def test_empty(self):
        unfiltered_artists = []
        URIs = self.searcher.filter_list_of_artists(unfiltered_artists)
        self.assertEqual(len(URIs), 0)

    def test_exact_match(self):
        unfiltered_artists = ['A$AP ROCKY']
        URIs = self.searcher.filter_list_of_artists(unfiltered_artists)
        self.assertEqual(URIs, ['spotify:artist:13ubrt8QOOCPljQ2FL1Kca'])

    def test_non_match(self):
        unfiltered_artists = ['asdfasdf']
        URIs = self.searcher.filter_list_of_artists(unfiltered_artists)
        self.assertEqual(len(URIs), 0)

    def test_incomplete_match(self):
        unfiltered_artists = ['Beach Boys'] # As opposed to The Beach Boys
        URIs = self.searcher.filter_list_of_artists(unfiltered_artists)
        self.assertEqual(URIs, ['spotify:artist:3oDbviiivRWhXwIE8hxkVV'])

    def test_one_good_one_bad(self):
        unfiltered_artists = ['U2', 'adfadfjkn;n']
        URIs = self.searcher.filter_list_of_artists(unfiltered_artists)
        self.assertEqual(URIs, ['spotify:artist:51Blml2LZPmy7TTiAg47vQ'])

class test_filter_artist(TestCase):
    """
    Test how accurately we get a good artist match from a name

    Test for num matches being 0, 1, or multiple
    """

    def setUp(self):
        self.searcher = spotifyHandler.SpotifySearcher()

    def test_bad_match(self):
        artist_name = 'adfajdnfpaj'
        URI = self.searcher.filter_artist(artist_name)
        self.assertEqual(URI, None)

    def test_one_exact_match(self):
        artist_name = 'Fitz and The Tantrums'
        URI = self.searcher.filter_artist(artist_name)
        self.assertEqual(URI, 'spotify:artist:4AcHt3JxKy59IX7JNNlZn4')

    def test_one_close_match(self):
        artist_name = 'Fitz The Tantrums'
        URI = self.searcher.filter_artist(artist_name)
        self.assertEqual(URI, 'spotify:artist:4AcHt3JxKy59IX7JNNlZn4')

    def test_exact_match_from_many(self):
        artist_name = 'The National'
        URI = self.searcher.filter_artist(artist_name)
        self.assertEqual(URI, 'spotify:artist:2cCUtGK9sDU2EoElnk0GNB')

    def test_close_match_from_many(self):
        artist_name = 'National'
        URI = self.searcher.filter_artist(artist_name)
        self.assertEqual(URI, 'spotify:artist:2cCUtGK9sDU2EoElnk0GNB')

class test_get_song_list(TestCase):
    """
    Make sure we are getting a good list of songs for a given artist

    Validate number of tracks per artist calculation for different N and len(artist_uris)
    Validate number of total tracks is equal to N for different N, len(artist_uris)
    validate that shuffling tracks does something
    """

    def setUp(self):
        self.searcher = spotifyHandler.SpotifySearcher()
        self.N = 99
        # 107 valid artists:
        self.artist_URIs = [u'spotify:artist:5wbIWUzTPuTxTyG6ouQKqz', u'spotify:artist:6IRouO5mvvfcyxtPDKMYFN',
                       u'spotify:artist:5K4W6rqBFWDnAN6FQUkS6x', u'spotify:artist:5K4W6rqBFWDnAN6FQUkS6x',
                       u'spotify:artist:3Z02hBLubJxuFJfhacLSDc', u'spotify:artist:5nLYd9ST4Cnwy6NHaCxbj8',
                       u'spotify:artist:3MdG05syQeRYPPcClLaUGl', u'spotify:artist:3YQKmKGau1PzlVlkL1iodx',
                       u'spotify:artist:3YQKmKGau1PzlVlkL1iodx', u'spotify:artist:5wbIWUzTPuTxTyG6ouQKqz',
                       u'spotify:artist:5dbuFbrHa1SJlQhQX9OUJ2', u'spotify:artist:32zks9ovi0IExzUd1C7W6o',
                       u'spotify:artist:5wbIWUzTPuTxTyG6ouQKqz', u'spotify:artist:41SQP16hv1TioVYqdckmxT',
                       u'spotify:artist:4Q82S0VzF8qlCb4PnSDurj', u'spotify:artist:44NX2ffIYHr6D4n7RaZF7A',
                       u'spotify:artist:16oZKvXb6WkQlVAjwo2Wbg', u'spotify:artist:1EevBGfUh3RSQSGpluxgBm',
                       u'spotify:artist:1l9d7B8W0IHy3LqWsxP2SH', u'spotify:artist:2WX2uTcsvV5OnS0inACecP',
                       u'spotify:artist:2EMAnMvWE2eb56ToJVfCWs', u'spotify:artist:3MdG05syQeRYPPcClLaUGl',
                       u'spotify:artist:02da1vDJ2hWqfK7aJL6SJm', u'spotify:artist:1OKOTYGoCE2buxTYMegJp7',
                       u'spotify:artist:35YNL4wwv11ZkmeWWL51y7', u'spotify:artist:1eVEVL20zNLcGrPDOR691N',
                       u'spotify:artist:6zB02lwP6L6ZH32nggQiJT', u'spotify:artist:4KlYg0F5KG9QNDFKaeTNAy',
                       u'spotify:artist:7ai5TWiOG8g9Hds5AATS28', u'spotify:artist:0fgYKF9Avljex0L9Wt5b8Z',
                       u'spotify:artist:0GDGKpJFhVpcjIGF8N6Ewt', u'spotify:artist:5OfhOoKunSnuubxxRML8J3',
                       u'spotify:artist:3EhbVgyfGd7HkpsagwL9GS', u'spotify:artist:1FGH4Bh7g9W6V4fUcKZWp5',
                       u'spotify:artist:4DeF1n7pWrs52PhWd2sEyr', u'spotify:artist:5WUlDfRSoLAfcVSX1WnrxN',
                       u'spotify:artist:05fo024EFotg9songSENOZ', u'spotify:artist:44NX2ffIYHr6D4n7RaZF7A',
                       u'spotify:artist:44NX2ffIYHr6D4n7RaZF7A', u'spotify:artist:2d3VHzlOEwXvmBdS4pzOPL',
                       u'spotify:artist:5E7zSu46SqTmgKqsc0tFkY', u'spotify:artist:2UDplVRprMbazU74Hq8OLl',
                       u'spotify:artist:4j7EVY3kuDwLPfD2jfC7LC', u'spotify:artist:50JJSqHUf2RQ9xsHs0KMHg',
                       u'spotify:artist:54SHZF2YS3W87xuJKSvOVf', u'spotify:artist:54SHZF2YS3W87xuJKSvOVf',
                       u'spotify:artist:25u4wHJWxCA9vO0CzxAbK7', u'spotify:artist:0FOWNUFHPnMy0vOw1siGqi',
                       u'spotify:artist:3VNITwohbvU5Wuy5PC6dsI', u'spotify:artist:3u1ulLq00Y3bfmq9FfjsPu',
                       u'spotify:artist:4Q82S0VzF8qlCb4PnSDurj', u'spotify:artist:4j56EQDQu5XnL7R3E9iFJT',
                       u'spotify:artist:1c4rxrxy8eDLvMVL1DTiBe', u'spotify:artist:0nJUwPwC9Ti4vvuJ0q3MfT',
                       u'spotify:artist:3u1ulLq00Y3bfmq9FfjsPu', u'spotify:artist:5u3A3inCFA998oODFCRk6S',
                       u'spotify:artist:3WGpXCj9YhhfX11TToZcXP', u'spotify:artist:5e1BZulIiYWPRm8yogwUYH',
                       u'spotify:artist:6qiGjRyN7TJ1GA2nXF68Hi', u'spotify:artist:1tpXaFf2F55E7kVJON4j4G',
                       u'spotify:artist:3vDpQbGnzRbRVirXlfQagB', u'spotify:artist:0AiTwNtYX8m4uhfU7rJ8RD',
                       u'spotify:artist:2ycnb8Er79LoH2AsR5ldjh', u'spotify:artist:3vDpQbGnzRbRVirXlfQagB',
                       u'spotify:artist:2vm8GdHyrJh2O2MfbQFYG0', u'spotify:artist:4X42BfuhWCAZ2swiVze9O0',
                       u'spotify:artist:7jdFEYD2LTYjfwxOdlVjmc', u'spotify:artist:1anyVhU62p31KFi8MEzkbf',
                       u'spotify:artist:3kVUvbeRdcrqQ3oHk5hPdx', u'spotify:artist:3wury2nd8idV4GecUg5xze',
                       u'spotify:artist:63MQldklfxkjYDoUE4Tppz', u'spotify:artist:1M3BVQ36cqPQix8lQNCh4K',
                       u'spotify:artist:41SQP16hv1TioVYqdckmxT', u'spotify:artist:6PjV05LlULv9XmFu7HeAia',
                       u'spotify:artist:1M3BVQ36cqPQix8lQNCh4K', u'spotify:artist:3AmgGrYHXqgbmZ2yKoIVzO',
                       u'spotify:artist:4AcHt3JxKy59IX7JNNlZn4', u'spotify:artist:1rXr1ZnvbRoYBaedIl9v4v',
                       u'spotify:artist:39vLtR3P6ltjthQKPc2gqy', u'spotify:artist:2CIhA8Jh3xrpFrHYMjYzBy',
                       u'spotify:artist:1mkuxdmqLdlrtCSwLQ2sUn', u'spotify:artist:1Ha0Fz4i0d4gu5fZbhBCtH',
                       u'spotify:artist:5YkaiMo0QXuVtdWycChYSP', u'spotify:artist:0OdUWJ0sBjDrqHygGUXeCF',
                       u'spotify:artist:2TI7qyDE0QfyOlnbtfDo7L', u'spotify:artist:5INjqkS1o8h1imAzPqGZBb',
                       u'spotify:artist:2TI7qyDE0QfyOlnbtfDo7L', u'spotify:artist:2uYWxilOVlUdk4oV9DvwqK',
                       u'spotify:artist:0jJNGWrpjGIHUdTTJiIYeB', u'spotify:artist:630wzNP2OL7fl4Xl0GnMWq',
                       u'spotify:artist:7wg1qvie3KqDNQbAkTdbX0', u'spotify:artist:11mqrDSFRRz8g0Wb3syJj5',
                       u'spotify:artist:6mcrZQmgzFGRWf7C0SObou', u'spotify:artist:1I4ovOpaXEwN05tFFvQDpP',
                       u'spotify:artist:32rtQaUBGDTxYH3rMWKNvH', u'spotify:artist:5SjNVG3L9mgWQPsfp1sFDB',
                       u'spotify:artist:2FZrEn80eCoWrrkGXPLF0v', u'spotify:artist:3mXI2gpwWnNO9qbQG3n3EP',
                       u'spotify:artist:1mFX1QlezK1lNPKQJkhwWb', u'spotify:artist:5RNFFojXkPRmlJZIwXeKQC',
                       u'spotify:artist:5INjqkS1o8h1imAzPqGZBb', u'spotify:artist:6DoH7ywD5BcQvjloe9OcIj',
                       u'spotify:artist:1l8Fu6IkuTP0U5QetQJ5Xt', u'spotify:artist:16GcWuvvybAoaHr0NqT8Eh',
                       u'spotify:artist:4dpARuHxo51G3z768sgnrY', u'spotify:artist:2cCUtGK9sDU2EoElnk0GNB',
                       u'spotify:artist:6urkHDoIVO1WO8vNIwcJmM']
        print("Running tests that search for songs. This takes a while, about 15 sec per search...")

    def test_more_songs_than_artists(self):
        self.artist_URIs = self.artist_URIs[0:30]
        list = self.searcher.get_song_list(self.artist_URIs, N=90, order="shuffled")
        self.assertEqual(len(list), 90)

    def test_more_artists_than_songs(self):
        self.artist_URIs = self.artist_URIs[0:90]
        list = self.searcher.get_song_list(self.artist_URIs, N=30, order="shuffled")
        self.assertEqual(len(list), 30)

    def test_way_more_artists_than_songs(self):
        """If the ratio of songs to artists is greater than 10, saturate to 10"""
        self.artist_URIs = self.artist_URIs[0:8]
        list = self.searcher.get_song_list(self.artist_URIs, N=90, order="shuffled")
        self.assertEqual(len(list), 80)

    def test_shuffle(self):
        """Verify that two requests for a shuffled song list come back in a different order"""

        list1 = self.searcher.get_song_list(self.artist_URIs, N=self.N, order="shuffled")
        list2 = self.searcher.get_song_list(self.artist_URIs, N=self.N, order="shuffled")
        self.assertNotEqual(list1,list2)


class test_find_top_tracks(TestCase):
    """
    Test to make sure we can get top tracks for an artist

    test variable numbers of requests
    """
    def setUp(self):
        self.artist = 'spotify:artist:2cCUtGK9sDU2EoElnk0GNB'
        self.searcher = spotifyHandler.SpotifySearcher()

    def test_find_0_tracks(self):
        tracklist = self.searcher.find_top_tracks(self.artist, 0)
        self.assertEqual(tracklist, [])

    def test_find_1_track(self):
        tracklist = self.searcher.find_top_tracks(self.artist, 1)
        self.assertEqual(len(tracklist), 1)

    def test_find_10_tracks(self):
        tracklist = self.searcher.find_top_tracks(self.artist, 10)
        self.assertEqual(len(tracklist), 10)

    def test_find_100_tracks(self):
        """ Make sure number of tracks is saturated to 10"""
        tracklist = self.searcher.find_top_tracks(self.artist, 100)
        self.assertEqual(len(tracklist), 10)

class test_init_login(TestCase):
    def setUp(self):
        self.pc = spotifyHandler.PlaylistCreator()

    def test_init_login_returned_url(self):
        url = self.pc.init_login()
        self.assertTrue('https://accounts.spotify.com/authorize?scope=playlist-modify-public&redirect_uri=' in url)

    def test_init_login_has_required_credentials(self):
        url = self.pc.init_login()
        self.assertNotEqual(self.pc.sp_oauth.client_secret, None)

class test_login(TestCase):
    """ Not sure how to test this without the UI and code..."""
    pass

class test_cli_login(TestCase):
    """ Not sure how to test this without the UI and code..."""
    pass

class test_mess_with_playlists(TestCase):
    def setUp(self):
        self.pc = spotifyHandler.PlaylistCreator()
        self.username = 'nickspeal_test'
        self.playlist_name = 'musicThisWeek_test'
        self.playlist_url = u'http://open.spotify.com/user/nickspeal_test/playlist/0EoNvCWUt0OMQ2XSOy0sTC'
        self.pc.cli_login(self.username)

    def test_find_existing_playlist(self):
        url = self.pc.get_spotify_playlist(self.playlist_name)
        print url
        self.assertEqual(url, self.playlist_url)

    # Cannot test creation of a non-existent playlist because it would be annoying to clutter up with lots of playlists.

    def test_erase_playlist(self):
        self.pc.erase(self.playlist_url)
        response = self.pc.sp.user_playlist(self.username, self.playlist_url)
        # Not sure how to get number of items from this...

    def test_add_to_playlist(self):
        song_list = [u'spotify:track:7rbCL7W893Zonbfnevku5s', u'spotify:track:6gf7WF9nXNON9HdNtrdEDq', u'spotify:track:0QEHU0ZccfSXYUpF2iVUab', u'spotify:track:6XW2rKHwNnX5qzk79Qis9w', u'spotify:track:20byjuLA86KfF9qjzxiwWG', u'spotify:track:61yQP9FDS7ukp4eAVTdwit', u'spotify:track:64zdnlftDUEpPQbOut0sV2', u'spotify:track:2h0L6HcKZLpzEabxqQD8nH', u'spotify:track:6OQip5XRRwqZJVFEJu8UTM', u'spotify:track:1rEEgRINO05qGniV12qiZP']

        self.pc.erase(self.playlist_url)
        self.pc.add(self.playlist_url, song_list)
        response = self.pc.sp.user_playlist(self.username, self.playlist_url)
        # Not sure how to get number of items from this...

class test_cache_artists(TestCase):
    def setUp(self):
        self.searcher = spotifyHandler.SpotifySearcher()

    def test_add_artist(self):
        self.assertEqual(Artist.objects.count(), 0)
        self.searcher.filter_list_of_artists(['Elvis Presley', 'Bon Iver', 'Kendrick Lamar'])
        self.assertEqual(Artist.objects.count(), 3)

    def test_add_fake_artist(self):
        self.assertEqual(Artist.objects.count(), 0)
        self.searcher.filter_list_of_artists(['asdfasdf'])
        self.assertEqual(Artist.objects.get(name  = 'asdfasdf').spotify_uri, None)


    def test_uri_saved_correctly(self):
        self.assertEqual(Artist.objects.count(), 0)
        returned_artist_uri = self.searcher.filter_artist('Kanye West')
        self.assertEqual(Artist.objects.get(name = 'Kanye West').spotify_uri, returned_artist_uri)

    def test_duplicate_names_not_saved(self):
        self.assertEqual(Artist.objects.count(), 0)
        self.searcher.filter_list_of_artists(['Elvis Presley', 'Bon Iver', 'Kendrick Lamar'])
        self.assertEqual(Artist.objects.count(), 3)
        self.searcher.filter_list_of_artists(['Elvis Presley', 'Bon Iver', 'Kanye West'])
        self.assertEqual(Artist.objects.count(), 4)

    def test_variant_spellings_both_saved(self):
        self.assertEqual(Artist.objects.count(), 0)
        self.searcher.filter_list_of_artists(['Kanye West'])
        self.assertEqual(Artist.objects.count(), 1)
        #this should make a new row for "Kanye" because lookup in DB cannot handle variant spellings
        self.searcher.filter_list_of_artists(['Kanye'])
        self.assertEqual(Artist.objects.count(), 2)
