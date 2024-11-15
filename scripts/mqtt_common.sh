#!/usr/bin/env sh

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# Parse common command line arguments
parse_common_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --skip-tls) SKIP_TLS=1; shift ;;
            --admin) ADMIN_MODE=1; shift ;;
            --driver) DRIVER="$2"; shift 2 ;;
            --response) RESPONSE_MODE=1; shift ;;
            *) return ;;  # Stop at unknown arg
        esac
    done
}

# Setup MQTT connection parameters
setup_mqtt_connection() {
    # Set default MQTT host
    if [ -z "$MQTT_HOST" ]; then
        MQTT_HOST=telemetry.b4mad.racing
    fi
    CLIENT_ID=$(hostname)-$$

    # Configure TLS
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
    elif [ -n "$DRIVER" ]; then
        USERNAME="$DRIVER"
        # Convert driver name to uppercase for env var
        DRIVER_UPPER=$(echo "$DRIVER" | tr '[:lower:]' '[:upper:]')
        PASSWORD_VAR="CLI_MQTT_${DRIVER_UPPER}_PASSWORD"
        PASSWORD=${!PASSWORD_VAR:-$DRIVER}
    else
        USERNAME=${CLI_CREWCHIEF_USER:-crewchief}
        PASSWORD=${CLI_CREWCHIEF_PASSWORD:-crewchief}
    fi
}
