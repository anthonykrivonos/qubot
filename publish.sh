#!/usr/bin/env sh

python3 -m pip install --user --upgrade setuptools wheel
python3 -m pip install --user --upgrade twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository pypi dist/*
rm -rf build
rm -rf dist
rm -rf qubot.egg-info
