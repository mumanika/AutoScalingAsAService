#!/bin/bash

# Desc: Remove the tenant namespace and also delete the routes to the remote IPs from the Provider namespace
# Args: namespace name, the remote IP on the other site, this sites source address with mask, destination sites address with mask

if [ $# -ne 4 ];
then
	exit
fi

ip netns delete $1
rm -rf /etc/netns/$1/*
src=$(echo $3 | cut -d '.' -f 1-3)
dst=$(echo $4 | cut -d '.' -f 1-3)
#rmdir /etc/netns/$1
ip netns exec Provider iptables -t filter -D FORWARD -i vProv -o Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -D FORWARD -o vProv -i Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -D FORWARD -s $src'.0/24' -d $dst'.0/24' -j ACCEPT
ip netns exec Provider iptables -t filter -D FORWARD -d $src'.0/24' -s $dst'.0/24' -j ACCEPT
ip netns exec Provider ip route delete $2
