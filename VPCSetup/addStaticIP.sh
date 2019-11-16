#!/bin/bash

# Desc: Append to the hostsfile to assign a static IP to the newly added VM
# Arguments: MAC address, VM name, IP address, namespace name, subnetName

if [ $# -ne 5 ];
then
	exit
fi

echo $1,$2,$3 >> /etc/netns/${4}/${5}.hostsfile
