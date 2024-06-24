#!/usr/bin/env sh

set -x
cd "$(dirname "$0")"
TIMESTAMP=$(gdate +%s%N)
# if TIMESTAMP is empty, use the date command
if [ -z "$TIMESTAMP" ]; then
  TIMESTAMP=$(date +%s%N)
fi

# create a random distance round track
DISTANCE_ROUND_TRACK=$(shuf -i 0-10000 -n 1)

TOPIC="/crewchief/durandom/1669233999/iRacing/sebring international/Ferrari 488 GT3 Evo 2021/Race"
T='{"CarModel": "Ferrari 488 GT3 Evo 2020",    "GameName": "iRacing",   "SessionId": "1669233672",    "SessionTypeName": "Race",    "TrackCode": "sebring international",    "Brake": 0.0,    "Clutch": 1.0,    "CurrentLap": 1.0,    "CurrentLapTime": 0.0,    "DistanceRoundTrack": 5564.84961,    "Gear": 3.0,    "Handbrake": 0.0,    "Rpms": 0.0,    "SpeedMs": 46.2075653,    "SteeringAngle": -0.232568219,    "Throttle": 0.995530248}'

TOPIC="replay/crewchief/durandom/1689266594/Automobilista 2/Taruma:Taruma_Internacional/Formula Vee/Qualify"
T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":'$DISTANCE_ROUND_TRACK',"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

# TOPIC="crewchief/Jim/1689266594/Automobilista 2/Taruma:Taruma_Internacional/Formula Vee/Qualify"
# T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":0.0,"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

if [ -z "$MQTT_HOST" ]; then
  MQTT_HOST=telemetry.b4mad.racing
  MQTT_HOST=mosquitto-mqtt
fi
CLIENT_ID=$(hostname)-$$

# check if MQTT_PORT is set
if [ -z "$MQTT_PORT" ]; then
  MQTT_PORT=1883
  # MQTT_PORT=31883
fi

mosquitto_pub -u crewchief -P crewchief \
  -t "$TOPIC" \
  -p $MQTT_PORT -h $MQTT_HOST -i $CLIENT_ID -d \
  -m "$T"
