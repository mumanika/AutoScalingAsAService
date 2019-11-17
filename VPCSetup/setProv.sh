#!/bin/bash

#set up the provider namespace, and the route to the other site's provider namespace on

#$1 is provider subnet ip (no mask), $2 is other site's provider subnet IP(no mask), $3 is the other site's hypervisor IP

if [ $# -ne 3 ];
then
	exit
fi

ip=$(echo $1 | cut -d '.' -f 1-3)

ip netns del Provider
ip netns add Provider
ip link add ProvDef type veth peer name DefProv
ip link set ProvDef netns Provider
ip netns exec Provider ip addr add ${ip}'.2/24' dev ProvDef
ip addr add ${ip}'.1/24' dev DefProv
ip netns exec Provider ip link set ProvDef up
ip link set DefProv up
ip netns exec Provider ip route add $(echo $2 | cut -d '.' -f 1-3).0/24 via ${ip}'.1'
ip route add $2'/24' via $3
brctl delif virbr0 vProv_
ip link del vProv_
ip link add vProv type veth peer name vProv_
ip link set vProv_ up
ip link set dev virbr0 up
brctl addif virbr0 vProv_
ip link set vProv netns Provider
ip netns exec Provider ip link set vProv up
ip netns exec Provider dhclient vProv 
ip netns exec Provider iptables -t filter -I FORWARD 1 -j DROP
ip netns exec Provider iptables -t nat -A POSTROUTING -o vProv -j MASQUERADE
