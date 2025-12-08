api:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi run softserve/api/main.py


dev:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi dev softserve/api/main.py


django:
	poetry run python manage.py runserver 8001


format:
	black softserve


migrate:
	poetry run python manage.py migrate


migrations:
	poetry run python manage.py makemigrations


shell:
	poetry run python manage.py shell


test:
	poetry run python manage.py test


# vim: set noexpandtab sts=0 ts=4:
