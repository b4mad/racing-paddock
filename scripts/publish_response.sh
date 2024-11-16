#!/usr/bin/env sh

# Source common MQTT functions
. "$(dirname "$0")/mqtt_common.sh"

# Parse command line arguments
parse_common_args "$@"

set -x
cd "$(dirname "$0")"

TOPIC="coach/durandom"
T='{"message": "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-Alaw-AFsp.wav", "priority": 9}'
T='{"message": "https://gitlab.com/mr_belowski/CrewChiefV4/-/raw/master/CrewChiefV4/sounds/driver_names/Ek.wav?inline=false", "priority": 9}'
T='{"message": "https://github.com/durandom/racing-assets/raw/main/speech.mp3", "priority": 9}'
T='{"message": "https://github.com/durandom/racing-assets/raw/main/speech.mp3", "priority": 9, "immediate": true}'
T='{"message": "brake normal gear 2", "priority": 9, "immediate": true}'
# T='{"message": "brake normal gear 2", "priority": 9, "distance": 31}'

# Setup MQTT connection parameters
setup_mqtt_connection

mosquitto_pub -u "$USERNAME" -P "$PASSWORD" \
  -t "$TOPIC" \
  -p $MQTT_PORT -h $MQTT_HOST $TLS_CERT_OPTS \
  -i $CLIENT_ID -d \
  -m "$T"
