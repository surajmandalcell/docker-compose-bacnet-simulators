#!/bin/bash

trap cleanup SIGINT

LOGS_PID=""

cleanup() {
    echo
    echo "Shutting down gracefully..."
    stop_logs
    docker compose down --timeout 2
    exit 0
}

run_dcu() {
    echo "Starting Docker Compose..."
    docker compose down --timeout 1
    docker compose build
    docker compose up -d
    echo "Docker Compose is running. Press 'r' to restart, 'e' to exit, or Ctrl+C to stop."
    show_logs
}

show_logs() {
    stop_logs
    docker compose logs -f &
    LOGS_PID=$!
}

stop_logs() {
    if [ ! -z "$LOGS_PID" ]; then
        kill $LOGS_PID 2>/dev/null
        wait $LOGS_PID 2>/dev/null
    fi
}

run_dcu

while true; do
    read -n 1 -r key

    case $key in
        r)
            echo
            echo "Restarting Docker Compose..."
            run_dcu
            ;;
        e)
            cleanup
            ;;
    esac
done