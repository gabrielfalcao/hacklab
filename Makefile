nosecmd := nosetests -sd --verbosity=2 --with-coverage --cover-package=hacklab

all:
	@make test

clear:
	@echo "Cleaning up files..."
	@find . -name '*.pyc' -exec rm -rf {} \;
	@echo "Cleaning up repositories..."
	@rm -rf repositories
	@echo "Cleaning up database file..."
	@rm -f database_hacklab.sqlite*

db: clear
	@echo "Cleaning up database ..."
	@echo "Creating database ..."
	@python -c 'import db;db.create_all()'

run: db
	@echo "Running bob builtin server..."
	@bob go

unit:
	@echo "Running unit tests ..."
	@$(nosecmd) tests/unit

functional: clear
	@echo "Running functional tests ..."
	@$(nosecmd) tests/functional

test:
	@echo "Running all (unit + functional) tests ..."
	@$(nosecmd) tests/unit tests/functional
