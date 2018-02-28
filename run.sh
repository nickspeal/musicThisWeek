source ./_private/spotipyCreds.sh
python manage.py makemigrations
python manage.py migrate
# open http://localhost:8888
python manage.py runserver 8888
