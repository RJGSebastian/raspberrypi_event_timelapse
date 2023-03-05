#!/usr/bin/env bash

echo "Installing raspberrypi_event_timelapse to /opt/raspberrypi_event_timelapse"

sudo mkdir -p "/opt/raspberrypi_event_timelapse"

# moving script
echo "Copying files to installation directory..."
sudo cp "$PWD/raspberrypi_event_timelapse.py" "/opt/raspberrypi_event_timelapse/"

# moving service file
echo "Copying service files to systemd directory"
sudo cp "$PWD/raspberrypi_event_timelapse.service" "/etc/systemd/system"

# enabling systemd service
echo "Enabling service..."
sudo systemctl enable raspberrypi_event_timelapse.service

install_missing_packages()
{
  msg=$'The following packages are missing:\n\t'"$*"$'\nDo you want to install them? [Y/n]:'

  read -p "$msg" answer

  if [[ "$answer" =~ [Yy] ]]; then
    echo "Missing packages will be installed..."
    # shellcheck disable=SC2068
    apt-get install $@
  else
    echo "Missing packages will not be installed, stopping installation..."
    return "3" 2>/dev/null || exit "3"
  fi
}

echo "Checking for required packages to install"
required_packages=("python3" "python3-pip")

export LANG=en_US.UTF-8 # language of next command to search for not installed packages breaks when output is in another language

# shellcheck disable=SC2119
# shellcheck disable=SC2068
pkgs=$(dpkg -l ${required_packages[@]} 2>&1 | awk '{if (/^D|^\||^\+/) {next} else if(/^dpkg-query:/) { print $6} else if(!/^[hi]i/) {print $2}}')

if [[ "$pkgs" != "" ]]; then
  # shellcheck disable=SC2068
  install_missing_packages ${pkgs[@]}
else
  echo "no packages need to be installed."
fi

echo "Installing necessary python packages"

required_python_packages=("ephem" "datetime" "platform" "time" "subprocess" "os" "gpiozero")
# installing python packages
# shellcheck disable=SC2068
sudo /usr/bin/env pip3 install ${required_python_packages[@]}

echo "Starting service"
sudo systemctl start raspberrypi_event_timelapse

echo "Installation completed."
