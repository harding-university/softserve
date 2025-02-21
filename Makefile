api:
	poetry run fastapi run softserve/api/main.py


dev:
	poetry run fastapi dev softserve/api/main.py


django:
	poetry run python manage.py runserver 8001


migrations:
	poetry run python manage.py makemigrations


migrate:
	poetry run python manage.py migrate


test:
	poetry run pytest -s


format:
	black softserve


# vim: set noexpandtab sts=0 ts=4:
