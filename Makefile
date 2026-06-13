secret_key:
	python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'

shell:
	python manage.py shell

server:
	python manage.py runserver
