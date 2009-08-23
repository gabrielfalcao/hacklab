nosecmd := nosetests -sd --with-coverage --cover-package=hacklab

all:
	@make test

db:
	@echo "Creating database ..."
	@python -c 'import db;db.create_all()'

unit:
	@echo "Running unit tests ..."
	@$(nosecmd) tests/unit

functional:
	@echo "Running functional tests ..."
	@$(nosecmd) tests/functional

test:
	@echo "Running all (unit + functional) tests ..."
	@$(nosecmd) tests/unit tests/functional