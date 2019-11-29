#!/bin/bash

# Create an iptables entry for loadbalancing for a particular group. This adds an iptable entry in the main PREROUTING chain which then branches into the custom chain created specifically for the group. Groups are mentioned by the tenants.
# Args: Balancing group name, Public exposed IP for the tenant i.e. the egress interface for the tenant namespace (this is different for different sites), unique port number for this group, namespace of the tenant

if [ $# -ne 4 ];
then
	exit
fi

ip netns exec $4 iptables -N $1  
ip netns exec $4 iptables -t nat -A PREROUTING -p tcp -d $2 --dport $3 -m state --state NEW -j $1
