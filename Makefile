api:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi run softserve/api/main.py


dev:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi dev softserve/api/main.py


docs:
	pandoc -o docs/integration-guide.html docs/integration-guide.md
	pandoc -o docs/integration-guide.pdf docs/integration-guide.md

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


.PHONY: api dev docs django format migrate migrations shell test

# vim: set noexpandtab sts=0 ts=4:
