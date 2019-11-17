#!/bin/bash

# Desc: This script creates a GRE tunnel device on ONE namespace and also adds the route to the remote IP in the Provider namespace
# Args: namespace name, tunnel name, local source IP, remote IP, next hop to the remote IP in the Provider namespace, next hop to the remote IP in the provider namespace from the current hypervisor

if [ $# -ne 6 ];
then
	exit
fi

ip=$(echo $4 | cut -d '.' -f 1-3)
ip netns exec $1 ip tunnel add $2 mode gre local $3 remote $4
ip netns exec $1 ip link set dev $2 up
ip netns exec Provider ip route add ${ip}.0/24 via $5
ip route add ${ip}.0/24 via $6
