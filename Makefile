api:
	poetry run fastapi run softserve/api/main.py


dev:
	poetry run fastapi dev softserve/api/main.py


test:
	poetry run pytest -s


format:
	black softserve


# vim: set noexpandtab sts=0 ts=4:
