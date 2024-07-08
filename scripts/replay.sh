#!/usr/bin/env sh

set -x

# OPTS="--live" SESSION_ID="1689266594" ./scripts/replay.sh

pipenv run ./manage.py replay --session-id $SESSION_ID $OPTS
