#!/usr/bin/env bash

echo "Installing raspberrypi_event_timelapse to /opt/raspberrypi_event_timelapse"

sudo mkdir "/opt/raspberrypi_event_timelapse"

# moving script
echo "Copying files to installation directory..."
sudo cp $PWD/raspberrypi_event_timelapse.py "/opt/raspberrypi_event_timelapse/"

# moving service file
echo "Copying service files to systemd directory"
sudo cp $PWD/raspberrypi_event_timelapse.service /etc/systemd/system

# enabling systemd service
echo "Enabling service..."
sudo systemctl enable raspberrypi_event_timelapse.service

# checking for python3 installation (https://stackoverflow.com/a/22592801/12322699)
echo "checking python3 installation..."
if [ $(dpkg-query -W -f='${Status}' python3 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
  # python3 not installed
  echo "installing python3..."
  apt-get install python3;
fi

echo "Starting service"
sudo systemctl start raspberrypi_event_timelapse

echo "Installation completed."
