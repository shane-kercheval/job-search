####
# Project
####
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
