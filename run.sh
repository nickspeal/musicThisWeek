source ./_private/spotipyCreds.sh
python manage.py makemigrations
python manage.py migrate
redis-server & python manage.py runserver 8888 & python manage.py runworker search
