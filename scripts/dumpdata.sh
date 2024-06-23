#!/usr/bin/env sh

set -x
cd "$(dirname "$0")/.."
pwd

models="game car track sessiontype session driver coach fastlap fastlapsegment lap trackguide trackguidenote landmark"
# models="trackguide trackguidenote"
# models="fastlap fastlapsegment"
models=""
for o in $models; do
  pipenv run ./manage.py dumpdata --indent 2 telemetry.$o > telemetry/fixtures.all/$o.json
done

pks="703,157,1237,15,1808,4021,1591,8787"
o="fastlap"
pipenv run ./manage.py dumpdata --indent 2 telemetry.$o --pks=$pks > telemetry/fixtures.all/$o.json

models="copilot copilotinstance profile"
models=""
for o in $models; do
  pipenv run ./manage.py dumpdata --indent 2 b4mad_racing_website.$o > b4mad_racing_website/fixtures/$o.json
done
