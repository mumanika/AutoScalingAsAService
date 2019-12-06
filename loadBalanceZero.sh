#!/bin/bash

# Desc: Zero the counters of the  nat chain for a namespace
# Args: namespace name

if [ $# -ne 1 ]
then
	echo "Illegal number of parameters"
	exit
fi

ip netns exec $1 iptables -t nat -Z PREROUTING
