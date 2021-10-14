#!/usr/bin/env bash

set -e # exit on error

# you can change this path
dir="/opt/raspberrypi_event_timelapse/logs"
mkdir -p "${dir}"

logfile="${dir}/log_$(date +%Y-%m-%d-%H-%M)"
echo "logfile of this session: ${logfile}"

# starting script
sudo /usr/bin/env python3 /opt/raspberrypi_event_timelapse/raspberrypi_event_timelapse.py > "${logfile}"

# see: https://unix.stackexchange.com/a/496370
