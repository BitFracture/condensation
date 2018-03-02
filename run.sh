#!/bin/bash

echo "\nCreating virtual environment\n"
pip3.exe install virtualenv --user
python3.exe -m venv ./.virtualenv

echo "\nRunning virtual environment\n"
./.virtualenv/Scripts/activate py35

cd condensation-forum

echo "Installing prerequisites\n"
pip3 install -r requirements.txt
echo "\nRunning application\n"
python3 ./application.py

cd ..

call ./.virtualenv/Scripts/deactivate
