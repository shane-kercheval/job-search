####
# docker commands
####
docker_build:
	docker compose -f docker-compose.yml build

docker_run: docker_build
	docker compose -f docker-compose.yml up

docker_down:
	docker compose down --remove-orphans

docker_rebuild:
	docker compose -f docker-compose.yml build --no-cache

docker_zsh:
	# run container and open up zsh command-line
	docker exec -it python-helpers-bash-1 /bin/zsh

docker_tests:
	# run tests within docker container
	docker compose run --no-deps --entrypoint "make tests" bash


####
# Project
####
environment:
	python3 -m venv .venv

clean:
	rm -rf .venv

linting:
	flake8 --max-line-length 99 source
	flake8 --max-line-length 99 tests

tests: linting
	rm -f tests/test_files/log.log
	# python -m unittest discover tests

	# python -m pytest tests
	coverage run -m pytest tests
	coverage html

open_coverage:
	open 'htmlcov/index.html'

data_extract:
	PYTHONPATH=. python source/service/etl.py

streamlit:
	PYTHONPATH=. python -m streamlit run source/entrypoints/streamlit_app.py
