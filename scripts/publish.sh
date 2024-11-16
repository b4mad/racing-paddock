#!/usr/bin/env sh

# Source common MQTT functions
. "$(dirname "$0")/mqtt_common.sh"

# Parse command line arguments
parse_common_args "$@"

set -x
cd "$(dirname "$0")"
TIMESTAMP=$(gdate +%s%N)
# if TIMESTAMP is empty, use the date command
if [ -z "$TIMESTAMP" ]; then
  TIMESTAMP=$(date +%s%N)
fi

# create a random distance round track
DISTANCE_ROUND_TRACK=$(shuf -i 0-10000 -n 1)

# TOPIC="crewchief/goern/1689266594/Automobilista 2/Taruma:Taruma_Internacional/Formula Vee/Qualify"
# T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":'$DISTANCE_ROUND_TRACK',"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

TOPIC="replay/crewchief/durandom/1689266594/Richard Burns Rally/Sardian Night/Renault Clio 16S Williams GrpA/Race"
T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":'$DISTANCE_ROUND_TRACK',"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

# # New Session
TOPIC="replay/crewchief/durandom/1689266594/Richard Burns Rally/Sardian Night/Renault Clio 16S Williams GrpA/NewSession"
TOPIC="crewchief/durandom/1689266594/Richard Burns Rally/Sardian Night/Renault Clio 16S Williams GrpA/NewSession"
T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":'$DISTANCE_ROUND_TRACK',"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

# TOPIC="crewchief/Jim/1689266594/Automobilista 2/Taruma:Taruma_Internacional/Formula Vee/Qualify"
# T='{"time": '$TIMESTAMP', "telemetry": {"Clutch":0.0,"Brake":1.0,"Throttle":0.0,"Handbrake":0.0,"SteeringAngle":-0.0103,"Rpms":0.0,"Gear":0,"SpeedMs":0.0,"DistanceRoundTrack":0.0,"WorldPosition_x":37.7886124,"WorldPosition_y":1.904185,"WorldPosition_z":-204.916718,"CurrentLap":1,"CurrentLapTime":-3.0,"LapTimePrevious":-1.0,"CurrentLapIsValid":false,"PreviousLapWasValid":true,"CarClass":"F_VEE"}}'

# Setup MQTT connection parameters
setup_mqtt_connection
mosquitto_pub -u $USERNAME -P $PASSWORD \
  -t "$TOPIC" \
  -p $MQTT_PORT -h $MQTT_HOST $TLS_CERT_OPTS \
  -i $CLIENT_ID -d \
  -m "$T"
