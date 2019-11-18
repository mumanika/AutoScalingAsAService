#!/bin/bash

# Desc: Add the route through the GRE tunnel
# Args: namespace name, ip address of intended destination with prefix, gre tunnel name

if [ $# -ne 3 ];
then
	exit
fi

ip netns exec $1 ip route add $2 dev $3
