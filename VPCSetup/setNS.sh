#!/bin/bash

# Desc: This script creates a new tenant namespace and connects it to the Provider. The default route is also given through the Provider.
# Arguments: namspace name, Egress interface subnet (.2 is given to namespace and .1 is given to the provider)

if [ $# -ne 2 ];
then
	exit
fi

ip=$(echo $2 | cut -d '.' -f 1-3)

ip netns del $1
ip netns add $1
ip link add ${1}Prov type veth peer name Prov$1
ip link set ${1}Prov netns $1
ip link set Prov$1 netns Provider
ip netns exec $1 ip addr add $ip'.2/24' dev ${1}Prov
ip netns exec $1 ip link set ${1}Prov up
ip netns exec Provider ip addr add $ip'.1/24' dev Prov$1
ip netns exec Provider ip link set Prov$1 up
ip netns exec $1 ip route add default via $ip'.1'

ip netns exec Provider iptables -t filter -I FORWARD 1 -i vProv -o Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -o vProv -i Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -i ens4 -o Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -o ens4 -i Prov$1 -j ACCEPT

mkdir /etc/netns/
mkdir /etc/netns/${1}/
