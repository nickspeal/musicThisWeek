from django.conf.urls import url, include
from music_this_week_app import views

urlpatterns = [
    url(r'^create', views.Create.as_view(), name="create")
