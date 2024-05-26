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
if [[ $EUID -ne 0 ]]; then
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
  if [[ $INPUT == "y" || $INPUT == "Y" ]]; then
    return 0
  fi

  return 1
}

download() {
  echo "Downloading the repository as a ZIP file ..."
  curl -Ls -o master.zip "$GOPRO_URL/archive/refs/heads/master.zip"

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
	# check python v3
	if ! which python3 > /dev/null; then
	  if yes_no "Python 3 is required! Please install first (eg. 'apt install python3 python3-pip python3-venv')" "Install now?" ; then
		  apt install -y python3 python3-pip python3-venv
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
	if ! python3 -m venv --help > /dev/null; then
		if yes_no "Python Virtual Environment is required! Please install first (eg. 'apt install python3-venv')." "Install?"; then
			apt install -y python3-venv
		else
		  return 1
		fi
	fi

	if [ ! -d "$GOPRO_HOME/.venv" ]; then
	  if yes_no "Python virtual environment doesn't exists ('python3 -m venv .venv')" "Create?"; then
			python3 -m venv "$GOPRO_HOME/.venv"
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
	if [[ ! -z $INPUT ]]; then
		IF=$INPUT
	fi

	# which ip address?
	read -p "ip address [$IP]: " -r INPUT
	if [[ ! -z $INPUT ]]; then
		until [[ -z $INPUT || $INPUT =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,3}$ ]]; do
			echo "invalid format: a.b.c.d/m"
			read -p "ip address [$IP]: " -r INPUT
		done
		if [[ ! -z $INPUT ]]; then
			IP=$INPUT
		fi
	fi
	
	# which router ip address?
	read -p "router address [$R]: " -r INPUT
	if [[ ! -z $INPUT ]]; then
		until [[ -z $INPUT || $INPUT =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; do
			echo "invalid format: a.b.c.d"
			read -p "router address [$R]: " -r INPUT
		done
		if [[ ! -z $INPUT ]]; then
			R=$INPUT
		fi
	fi

	# which dns ip address?
	read -p "dns address [$DNS]: " -r INPUT
	if [[ ! -z $INPUT ]]; then
		until [[ -z $INPUT || $INPUT =~ ^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[ ]*)+$ ]]; do
			echo "invalid format: a.b.c.d"
			read -p "dns address [$DNS]: " -r INPUT
		done
		if [[ ! -z $INPUT ]]; then
			DNS=$INPUT
		fi
	fi
	
	# remove 'old' configuration
	remove_static_ip "$IF"

	# set the new configuration
	if [[ -f $DHCP_CONFIG ]]; then
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
dns=${DNS// /;};
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
  if [[ "${1-}" == "" ]]; then
      NAME=`cat $HOST_CONFIG`
      # ask for hostname
      read -p "New hostname [$NAME]: " -r INPUT
      if [[ ! -z $INPUT ]]; then
          NAME=$INPUT
      fi
  else
      NAME="$1"
  fi
	echo -e "$NAME" > $HOST_CONFIG

	sed -i '/^\s*127.0.1.1/ d' $HOSTS_CONFIG
	echo -e "127.0.1.1\t$NAME" >> $HOSTS_CONFIG

	REBOOT=true
}

remove_static_ip() {
	# remove existing configuration
	if [[ -f $DHCP_CONFIG ]]; then
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

  if [[ ! -f "$GOPRO_HOME/shell/install.sh" ]]; then
    download
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
    if [[ $? == 0 ]]; then
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
if [ "$REBOOT" == true ] ; then
	if yes_no "A reboot is required in order to complete installation. Reboot?"; then
		reboot
	fi
fi
