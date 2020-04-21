.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

isort: ## using isort to sort imports
	isort -rc -vb .

lint: ## check style with flake8
	flake8 topocalc

test: ## run tests quickly with the default Python
	python3 setup.py test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## run coverage and submit
	coverage run --source topocalc setup.py test
	coverage report --fail-under=85

coveralls: coverage ## run coveralls
	coveralls

coverage-html: coverage ## check code coverage quickly with the default Python
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/topocalc.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ topocalc
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload wheelhouse/topocalc*

dist: clean ## builds source and wheel package
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python3 setup.py install

jl: ## jupyter lab for analysis
	jupyter lab --no-browser --port=5678 --ip=0.0.0.0 --allow-root

gold_skew: ## gold skew files
	./tests/Lakes/gold_ipw/skew/make_gold_skew

gold_horizon: ## gold horizon files
	./tests/Lakes/gold_ipw/horizon/make_gold_horizon

gold_viewf: ## gold viewf files
	./tests/Lakes/gold_ipw/viewf/make_gold_viewf


