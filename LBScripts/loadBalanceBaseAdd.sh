#!/bin/bash

# Desc: Add iptable rules for load balancing for the particular LB group on the tenant base namespace. A group is made up of one or more subnet namespaces. (NOTE: make sure to add the route to the loopback interface here at the other site through the GRE tunnel) 
# Args: Every nth packet, Private subnet IP exposed to base namespace, Private subnet destination port, namespace name, load balancing group name

if [ $# -ne 5 ];
then
	echo "Illegal number of params"
	exit
fi

if [ $3 -ne 0 ];
then
	ip netns exec $4 iptables -t nat -I $5 1 -p tcp -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $2:$3
else
	ip netns exec $4 iptables -t nat -I $5 1 -p tcp -m state --state NEW -m statistic --mode nth --every $1 --packet 0 -j DNAT --to-destination $2
fi


