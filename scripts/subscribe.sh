#!/usr/bin/env sh

# Source common MQTT functions
. "$(dirname "$0")/mqtt_common.sh"

# Parse command line arguments
parse_common_args "$@"

set -x
cd "$(dirname "$0")"

# Setup MQTT connection parameters
setup_mqtt_connection

if [ ! -z "$DRIVER" ]; then
  DRIVER="${DRIVER}/"
fi

if [ -z "$MQTT_TOPIC" ]; then
  if [ -n "$RESPONSE_MODE" ]; then
    MQTT_TOPIC="coach/${DRIVER}#"
  else
    MQTT_TOPIC="crewchief/${DRIVER}#"
  fi
fi

mosquitto_sub -u $USERNAME -P $PASSWORD \
  -p $MQTT_PORT -h $MQTT_HOST $TLS_CERT_OPTS \
  -i $CLIENT_ID -d \
  -t $MQTT_TOPIC
