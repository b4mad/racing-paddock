#!/usr/bin/env sh

# Parse command line arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        --skip-tls) SKIP_TLS=1; shift ;;
        --admin) ADMIN_MODE=1; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
done

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

set -x
cd "$(dirname "$0")"
TIMESTAMP=$(gdate +%s%N)

TOPIC="/coach/durandom"
T='{"message": "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-Alaw-AFsp.wav", "priority": 9}'
T='{"message": "https://gitlab.com/mr_belowski/CrewChiefV4/-/raw/master/CrewChiefV4/sounds/driver_names/Ek.wav?inline=false", "priority": 9}'
T='{"message": "https://github.com/durandom/racing-assets/raw/main/speech.mp3", "priority": 9}'
T='{"message": "https://github.com/durandom/racing-assets/raw/main/speech.mp3", "priority": 9, "immediate": true}'
# T='{"message": "brake normal gear 2", "priority": 9}'
# T='{"message": "brake normal gear 2", "priority": 9, "distance": 31}'

if [ -z "$MQTT_HOST" ]; then
  MQTT_HOST=telemetry.b4mad.racing
fi
CLIENT_ID=$(hostname)-$$

# Configure TLS based on --skip-tls flag
if [ -z "$SKIP_TLS" ]; then
  MQTT_PORT=30883
  TLS_CERT_OPTS="--tls-use-os-certs"
else
  MQTT_PORT=31883
  TLS_CERT_OPTS=""
fi

# Set credentials based on admin mode
if [ -n "$ADMIN_MODE" ]; then
    USERNAME="admin"
    PASSWORD=${CLI_MQTT_ADMIN_PASSWORD:-admin}
else
    USERNAME="crewchief"
    PASSWORD="crewchief"
fi

mosquitto_pub -u "$USERNAME" -P "$PASSWORD" \
  -t "$TOPIC" \
  -p $MQTT_PORT -h $MQTT_HOST $TLS_CERT_OPTS \
  -i $CLIENT_ID -d \
  -m "$T"
