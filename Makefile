.PHONY: test

ci:
	py.test --junitxml=report.xml

test:
	python setup.py test

coverage:
	py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=manga_dl --junitxml=report.xml tests

flake8:
	flake8 --ignore=E501,F401,W503 manga_dl

clean:
	rm -fr build dist .egg pymanga_dl.egg-info \
	rm -fr .pytest_cache coverage.xml report.xml htmlcov\
	find . | grep __pycache__ | xargs rm -fr \
	find . | grep .pyc | xargs rm -f \

install:
	python setup.py install

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build .egg requests.egg-info
