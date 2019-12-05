#!/bin/bash

# Desc: Add the route through the device
# Args: ip address of intended destination with prefix, gre tunnel name, optional via address

if [ $# -lt 2 ];
then
	exit
fi

if [ $# -eq 3 ];
then
	ip route add $1 via $3 dev $2
else
	ip route add $1 dev $2
fi
