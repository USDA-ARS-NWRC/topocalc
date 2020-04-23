python3 setup.py sdist --formats=gztar
python3 -m pip install twine
python3 -m twine upload --skip-existing dist/*.tar.gz