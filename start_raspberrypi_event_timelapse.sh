#!/usr/bin/env bash

set -e # exit on error

# you can change this path
dir="$HOME/raspberrypi_event_timelapse_logs"
mkdir -p "${dir}"

# starting script
/usr/bin/env python3 /opt/raspberrypi_event_timelapse/raspberrypi_event_timelapse.py > "${dir}/log_$(date +%Y-%m-%d-%H-%M)"

# see: https://unix.stackexchange.com/a/496370
