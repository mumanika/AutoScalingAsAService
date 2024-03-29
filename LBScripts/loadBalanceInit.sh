#!/bin/bash

# Desc: Add iptable rules for load balancing. Add the entry for only new connections. Do this only on the control node's site.
# Args: Public Destination IP address, Public IP destination port, the IP address assigned to the loopback interface, namespace name

if [ $# -ne 4 ];
then
	echo "Illegal number of params"
	exit
fi

ip netns exec $4 iptables -t nat -A PREROUTING  -p tcp -d $1 --dport $2 -m state --state NEW -j DNAT --to-destination $3:$2
