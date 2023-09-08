appname = zkillboard
package = zkillboard
help:
	@echo "Makefile for $(appname)"

coverage:
	coverage run -m unittest discover -f -v && coverage html && coverage report -m

pylint:
	pylint $(package)

check_complexity:
	flake8 $(package) --max-complexity=10

flake8:
	flake8 $(package) --count
