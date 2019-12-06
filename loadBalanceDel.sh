#!/bin/bash

# Desc: Delete the nat rule for a namespace at the specified 
# Args: namespace name, position of the rule

if [ $# -ne 2 ]
then
	echo "Illegal number of parameters"
	exit
fi

ip netns exec $1 iptables -t nat -D PREROUTING $2
