nosecmd := nosetests -sd --with-coverage --cover-package=hacklab

all:
	@make test

db:
	@echo "Cleaning up database ..."
	@rm -f database_hacklab.sqlite
	@echo "Creating database ..."
	@python -c 'import db;db.create_all()'

run: db
	@echo "Running bob builtin server..."
	@bob go

unit:
	@echo "Running unit tests ..."
	@$(nosecmd) tests/unit

functional:
	@echo "Running functional tests ..."
	@$(nosecmd) tests/functional

test:
	@echo "Running all (unit + functional) tests ..."
	@$(nosecmd) tests/unit tests/functional
