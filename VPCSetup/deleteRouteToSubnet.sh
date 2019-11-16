#!/bin/bash

# Desc: 
# Args: namespace name, ip address of route with prefix, gre tunnel name

if [ $# -ne 3 ];
then
	exit
fi

ip netns exec $1 ip route delete $2 dev $3
