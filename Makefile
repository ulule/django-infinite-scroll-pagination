test:
	@(py.test -s --cov-report term --cov-config .coveragerc --cov=infinite_scroll_pagination --color=yes ./tests)

delpyc:
	@(find . -name '*.pyc' -delete)

release:
	@(python setup.py sdist register upload -s)
