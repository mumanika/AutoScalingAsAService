#!/bin/bash

#set up the provider namespace

#$1 is provider ip and $2 is neighbout ip /24format

ip netns del Provider
ip netns add Provider
ip link set ens4 netns Provider
ip netns exec Provider ip link set ens4 up
ip netns exec Provider ip addr add $1 dev ens4
ip netns exec Provider ip route add $(echo $1 | cut -d '.' -f 1-3).0/24 dev ens4
ip link add vProv type veth peer name vProv_
ip link set vProv_ up
brctl addif virbr0 vProv_
ip link set vProv netns Provider
ip netns exec Provider ip link set vProv up
ip netns exec Provider dhclient vProv 

