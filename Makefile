.PHONY: test

ci:
	py.test --junitxml=report.xml

test:
	python setup.py test

clean:
	rm -fr build dist .egg pymanga_dl.egg-info \
	rm -fr report.xml manga \
	find . | grep __pycache__ | xargs rm -fr \
	find . | grep .pyc | xargs rm -f \

install:
	python setup.py install

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build .egg requests.egg-info
