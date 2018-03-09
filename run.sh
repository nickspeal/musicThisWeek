source ./_private/spotipyCreds.sh
python manage.py makemigrations
python manage.py migrate
# redis-server & python manage.py runserver 8888 & python manage.py runworker search
echo "Be sure to run `redis-server` and `python manage.py runworker search song events` in other windows"
python manage.py runserver 8888
