####
# Project
####
linting:
	flake8 --max-line-length 99 source
	flake8 --max-line-length 99 tests

tests: linting
	rm -f tests/test_files/log.log
	#python -m unittest discover tests
	#pytest tests
	coverage run -m pytest tests
	coverage html

open_coverage:
	open 'htmlcov/index.html'

data_extract:
	python source/entrypoints/cli.py extract

data_transform:
	python source/entrypoints/cli.py transform

data: data_extract data_transform

exploration:
	jupyter nbconvert --execute --to html source/notebooks/data-profile.ipynb
	mv source/notebooks/data-profile.html output/data/data-profile.html

experiment_1:
	python source/entrypoints/cli.py run-experiment \
		-n_iterations=4 \
		-n_folds=3 \
		-n_repeats=1 \
		-score='roc_auc' \
		-random_state=3
	cp source/notebooks/experiment-template.ipynb source/notebooks/experiment_1.ipynb
	jupyter nbconvert --execute --to html source/notebooks/experiment_1.ipynb
	mv source/notebooks/experiment_1.html output/experiment_1.html
	rm source/notebooks/experiment_1.ipynb

remove_logs:
	rm -f output/log.log

## Run entire workflow.
all: data tests remove_logs exploration experiments
