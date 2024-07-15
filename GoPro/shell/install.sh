#!/bin/bash

set -eu

GOPRO_URL="https://github.com/BerlinUnited/RoboCupTools"
GOPRO_HOME=$(realpath "$(dirname "$(readlink -f -- "$0")")/..")
DHCP_CONFIG="/etc/dhcpcd.conf"
HOST_CONFIG="/etc/hostname"
HOSTS_CONFIG="/etc/hosts"
NM_NAME="GoPi"
REBOOT=false

#check if root first
if [ "${USER:-$(id -u -n)}" != "root" ]; then
   echo "This script must be run as root"
   exit 1
fi

############################################################################################
# FUNCTIONS
############################################################################################

yes_no() { # question, prompt
  if [ $# -gt 1 ]; then
    echo "$1";
    shift
  fi

  read -p "$1 [y|N]: " -r INPUT
  if [ "$INPUT" = "y" ] || [ "$INPUT" = "Y" ]; then
    return 0
  fi

  return 1
}

download() {
  echo "Downloading the repository as a ZIP file ..."
  if command -v "curl" > /dev/null; then
    curl -Ls -o master.zip "$GOPRO_URL/archive/refs/heads/master.zip"
  elif command -v "wget" > /dev/null; then
    wget -qO master.zip "$GOPRO_URL/archive/refs/heads/master.zip"
  else
    echo "Neither 'curl' nor 'wget' are available!"
    return 1
  fi

  if ! which unzip > /dev/null; then
    if yes_no "Unzip is required! Please install first (eg. 'apt install unzip')" "Install now?" ; then
      apt install -y unzip
    else
      return 1
    fi
  fi

  echo "Extract ZIP file ..."
  unzip -qq master.zip "RoboCupTools-master/GoPro/*" \
    && mkdir GoPro/ \
    && mv RoboCupTools-master/GoPro/* GoPro/

  echo "Cleanup download files"
  rm -rf RoboCupTools-master/

  # update the home directory variable
  cd GoPro
  GOPRO_HOME=$(pwd)
}

check_dependencies() {
  python=""
  # try to find a supported version (>= 3.9 && <= 3.11) -- required by the open_gopro dependency!
  python_executables="python3.11 python3.10 python3.9"
  for exe in $python_executables; do
    if command -v "$exe" > /dev/null; then
      python="$exe"
      break
    fi
  done
  # check python v3
  if [ -z "$python" ]; then
    # check available versions
    python=$(apt-cache search --names-only "^($(echo "$python_executables" | tr ' ' '|'))\$" | awk '{print $1}' | sort -t. -k2,2n | tail -n 1)
    if [ -z "$python" ]; then
      echo -e "\033[1;31mUnable to find a matching python version!\033[0m"
      return 1
    fi
    # install it
    if yes_no "Python 3 is required! Please install first (eg. 'apt install $python $python-dev $python-venv python3-pip')" "Install now?" ; then
      apt install -y "$python" "$python-dev" "$python-venv" python3-pip
    else
      return 1
    fi
  fi
  # check pip
  if ! which pip > /dev/null; then
    if yes_no "PIP is required! Please install first (eg. 'apt install python3-pip')." "Install?"; then
      apt install -y python3-pip
    else
      return 1
    fi
  fi
  # check python environment module
  if ! $python -m venv --help > /dev/null || ! $python -m ensurepip --help > /dev/null 2>&1; then
    if yes_no "Python Virtual Environment is required! Please install first (eg. 'apt install $python-venv')." "Install?"; then
      apt install -y "$python-venv"
    else
      return 1
    fi
  fi

  if [ ! -d "$GOPRO_HOME/.venv" ]; then
    if yes_no "Python virtual environment doesn't exists ('$python -m venv .venv')" "Create?"; then
      echo "Creating python virtual environment ..."
      $python -m venv "$GOPRO_HOME/.venv"
    else
      return 1
    fi
  fi

  if "$GOPRO_HOME/.venv/bin/pip" freeze --no-color -r "$GOPRO_HOME/requirements.txt" 2>&1 | grep -q "not installed" ; then
    if yes_no "Install required dependencies to virtual environment?" "Continue?"; then
      "$GOPRO_HOME/.venv/bin/pip" install -r "$GOPRO_HOME/requirements.txt"
    else
      return 1
    fi
  fi

  # everything 'ok'
  return 0
}

setup_static_ip() {
  # some defaults
  IF="eth0"
  IP="10.0.4.99/16"
  R="10.0.0.1"
  DNS="10.0.0.1 8.8.8.8"

  # which interface?
  read -p "interface [$IF]: " -r INPUT
  if [ -n "$INPUT" ]; then
    IF=$INPUT
  fi

  # which ip address?
  read -p "ip address [$IP]: " -r INPUT
  if [ -n "$INPUT" ]; then
    while [ -n "$INPUT" ] && ! echo "$INPUT" | grep -Eq '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,3}$'; do
      echo "invalid format: a.b.c.d/m"
      read -p "ip address [$IP]: " -r INPUT
    done
    if [ -n "$INPUT" ]; then
      IP=$INPUT
    fi
  fi

  # which router ip address?
  read -p "router address [$R]: " -r INPUT
  if [ -n "$INPUT" ]; then
    while [ -n "$INPUT" ] && ! echo "$INPUT" | grep -Eq '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; do
      echo "invalid format: a.b.c.d"
      read -p "router address [$R]: " -r INPUT
    done
    if [ -n "$INPUT" ]; then
      R=$INPUT
    fi
  fi

  # which dns ip address?
  read -p "dns address [$DNS]: " -r INPUT
  if [ -n "$INPUT" ]; then
    while [ -n "$INPUT" ] && ! echo "$INPUT" | grep -Eq '^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[ ]*)+$'; do
      echo "invalid format: a.b.c.d"
      read -p "dns address [$DNS]: " -r INPUT
    done
    if [ -n "$INPUT" ]; then
      DNS=$INPUT
    fi
  fi

  # remove 'old' configuration
  remove_static_ip "$IF"

  # set the new configuration
  if [ -f $DHCP_CONFIG ]; then
    echo -e "interface $IF\nstatic ip_address=$IP\nstatic routers=$R\nstatic domain_name_servers=$DNS\n" >> $DHCP_CONFIG
  else
    cat <<EOF > "/etc/NetworkManager/system-connections/$NM_NAME.nmconnection"
[connection]
id=$NM_NAME
uuid=$(uuid)
type=ethernet
interface-name=$IF

[ethernet]

[ipv4]
address1=$IP,$R
dns=$(echo "$DNS" | tr ' ' ';');
method=manual

[ipv6]
addr-gen-mode=default
method=auto

[proxy]
EOF
    chmod 600 "/etc/NetworkManager/system-connections/$NM_NAME.nmconnection"
  fi

  REBOOT=true
}

setup_hostname() {
  if [ -z "${1-}" ]; then
    NAME=$(cat "$HOST_CONFIG")
    # ask for hostname
    read -p "New hostname [$NAME]: " -r INPUT
    if [ -n "$INPUT" ]; then
      NAME=$INPUT
    fi
  else
    NAME="$1"
  fi

  echo "$NAME" > "$HOST_CONFIG"

  sed -i '/^[[:space:]]*127\.0\.1\.1/ d' "$HOSTS_CONFIG"
  echo "127.0.1.1\t$NAME" >> "$HOSTS_CONFIG"

  REBOOT=true
}

remove_static_ip() {
  # remove existing configuration
  if [ -f $DHCP_CONFIG ]; then
    sed -i '/^\s*interface/ d' $DHCP_CONFIG
    sed -i '/^\s*static ip_address/ d' $DHCP_CONFIG
    sed -i '/^\s*static routers/ d' $DHCP_CONFIG
    sed -i '/^\s*static domain_name_servers/ d' $DHCP_CONFIG
  else
    rm -f "/etc/NetworkManager/system-connections/$NM_NAME.nmconnection"
  fi
}

stop_service() {
  # helper for stopping the services
  if systemctl -q is-active "$1"; then
    echo "stopping $1"
    systemctl stop "$1" > /dev/null
  fi
}

install() {
  echo "Installing ..."

  if [ ! -f "$GOPRO_HOME/shell/install.sh" ]; then
    if [ ! -d "GoPro" ]; then
      download
    else
      echo "The installation directory 'GoPro' already exists"
      if yes_no "Use it for installation?"; then
        # update the home directory variable
        cd GoPro
        GOPRO_HOME=$(pwd)
      else
        echo "Remove it first or change directory!"
        return 1
    fi
  fi
  fi

  echo "Check required dependencies ..."
  if ! check_dependencies; then
    exit $?
  fi

  echo "Stopping running service ..."
  stop_service gopro

  echo "Create executable ..."
  ln -sf "$GOPRO_HOME/shell/gopro" /usr/bin/gopro
  chmod +x /usr/bin/gopro
  chmod +x $GOPRO_HOME/main.py

  echo "Install service ..."
  cp $GOPRO_HOME/shell/gopro.service /lib/systemd/system/
  chmod 644 /lib/systemd/system/gopro.service

  echo "Enable service ..."
  systemctl daemon-reload
  systemctl enable gopro.service

  echo "Start service ..."
  systemctl start gopro

  if yes_no "Setup (unique) hostname?"; then
    setup_hostname
  fi

  if yes_no "Setup static ip address?"; then
    setup_static_ip
  fi

  echo "finished!"
}

uninstall() {
  echo "uninstalling";

  stop_service gopro

  systemctl disable gopro.service

  rm -f /usr/bin/gopro /lib/systemd/system/gopro.service

  systemctl daemon-reload

  if yes_no "Set hostname (back) to 'raspberrypi'?"; then
    setup_hostname "raspberrypi"
  fi

  if yes_no "Remove static ip address configuration?"; then
    remove_static_ip
    REBOOT=true
  fi

  echo "FINSIH"
}

help() {
  echo "Install script for the GoPi application"
  echo -e "\t install \t installs everything needed to for running the GoPi permanently"
  echo -e "\t uninstall \t uninstalls everything"
  echo -e "\t check \t\t checks the required dependencies"
  echo -e "\t ip \t\t setups the static ip configuration only"
  echo -e "\t help \t\t shows this help"
}

############################################################################################
# MAIN
############################################################################################

case "${1-}" in
  ""|''|install)
    install
    ;;
  uninstall)
    uninstall
    ;;
  check)
    check_dependencies
    if [ $? -eq 0 ]; then
      echo "Success, ready to install!"
    fi
    ;;
  ip)
    echo "Setup static ip."
    setup_static_ip
    ;;
  help)
    help
    ;;
  *)
    echo -e "$0 (install|uninstall|check|ip|help)\n"
    help
    ;;
esac

############################################################################################
# POST-PROCESSING
############################################################################################

# check if we need to reboot
if [ "$REBOOT" = true ]; then
  if yes_no "A reboot is required in order to complete installation. Reboot?"; then
    reboot
  fi
fi
