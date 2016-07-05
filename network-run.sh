source ./_private/spotipyCreds.sh
export SPOTIPY_REDIRECT_URI='http://nick-personal.local:8888/callback'
open http://nick-personal.local:8888
python manage.py runserver nick-personal.local:8888
