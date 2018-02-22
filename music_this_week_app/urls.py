from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /
    url(r'^$', views.home, name='home'),
    # ex: /login/
    url(r'^login/$', views.login, name='login'),
    # ex: /setup/
    url(r'^setup/$', views.setup, name='setup'),
    # ex: /search/
    url(r'^search/$', views.search, name='search'),
    # ex: /callback/?code=gibberish
    url(r'^callback/$', views.callback, name='done')
]
