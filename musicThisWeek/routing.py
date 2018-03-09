from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
# from channels.auth import AuthMiddlewareStack

from music_this_week_app.consumers import SearchConsumer, SongAddConsumer, EventsConsumer, Subscribe

application = ProtocolTypeRouter({
     # Handled by the worker - Make sure to start the worker as a separate process with these channels as arguments!
    "channel": ChannelNameRouter({
        "search": SearchConsumer.SearchConsumer,
        "song": SongAddConsumer.SongAddConsumer,
        "events": EventsConsumer.EventsConsumer,
    }),
    # Handled by runserver automatically
    "websocket": URLRouter([
        url("^subscribe", Subscribe.Subscribe)
    ]),
})
