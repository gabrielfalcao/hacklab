nosecmd := nosetests -sd --with-coverage --cover-package=hacklab

all:
	@make test

unit:
	@echo "Running unit tests ..."
	@$(nosecmd) tests/unit

functional:
	@echo "Running functional tests ..."
	@$(nosecmd) tests/functional

test:
	@echo "Running all (unit + functional) tests ..."
	@$(nosecmd) tests/unit tests/functional