api-dev:
	poetry run fastapi dev softserve/api.py


test:
	poetry run pytest -s


format:
	black softserve


# vim: set noexpandtab sts=0 ts=4:
