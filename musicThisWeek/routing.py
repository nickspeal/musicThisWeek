from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
# from channels.auth import AuthMiddlewareStack

from music_this_week_app.backend import consumers

application = ProtocolTypeRouter({

    # WebSocket chat handler
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         url("^chat/admin/$", AdminChatConsumer),
    #         url("^chat/$", PublicChatConsumer),
    #     ])
    # ),
    "channel": ChannelNameRouter({
        "search": consumers.Search,
    }),
    "websocket": URLRouter([
        url("^subscribe", consumers.Subscribe)
    ])
})
