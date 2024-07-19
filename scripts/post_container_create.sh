#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y mosquitto-clients
sudo apt-get install -y postgresql-client
pipenv install --dev
pipenv run ./manage.py migrate
# pipenv run ./manage.py loaddata driver game car track landmark
# pipenv run ./manage.py loaddata session lap sessiontype
DJANGO_SUPERUSER_PASSWORD=admin pipenv run ./manage.py createsuperuser  --username admin --email admin@example.com --noinput || true
pipenv run ./manage.py loaddata driver game fastlap fastlapsegment landmark lap session sessiontype track trackguide trackguidenote coach car copilot copilotinstance profile user
pip install -U pre-commit && pre-commit install-hooks
