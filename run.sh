source ./_private/spotipyCreds.sh
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 8888
