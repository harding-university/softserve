api:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi run softserve/api/main.py


dev:
	DJANGO_SETTINGS_MODULE=project.settings poetry run fastapi dev softserve/api/main.py


docs:
	pandoc -o guides/creeper-notation.html guides/creeper-notation.md
	pandoc -o guides/creeper-notation.pdf guides/creeper-notation.md
	pandoc -o guides/event-guide.html guides/event-guide.md
	pandoc -o guides/event-guide.pdf guides/event-guide.md
	pandoc -o guides/integration-guide.html guides/integration-guide.md
	pandoc -o guides/integration-guide.pdf guides/integration-guide.md

django:
	poetry run python manage.py runserver 8001


format:
	black softserve
	prettier -w dashboard


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
