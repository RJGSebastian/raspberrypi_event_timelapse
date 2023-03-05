#!/usr/bin/env bash
echo $(date +%s)","$1","$(vcgencmd measure_temp) >> $2cpu_temps.csv
