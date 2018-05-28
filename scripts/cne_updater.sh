#!/usr/bin/env bash
#
# Craft N' Escape Updater
#
# Well, this script updates everything in Craft N' Escape, i.e source code, dependencies, etc.

set -e # Makes any subsequent failing commands to exit the script immediately

echo "## Initializing"

. venv/bin/activate
export FLASK_APP=cne.py

echo "## Updating dependencies"

pip install --upgrade --no-cache -r requirements.txt
pip install --upgrade --no-cache uwsgi

echo "## Pulling latest code version"

git pull

echo "## Restarting services"

chown -R www-data:www-data ./

supervisorctl restart craft-n-escape.com