#!/bin/bash

#set up the provider namespace

#$1 is provider ip and $2 is neighbout ip /24format

ip netns del Provider
ip netns add Provider
ip link set ens4 netns Provider
ip netns exec Provider ip link set ens4 up
ip addr add $1 dev ens4
ip route add default via $1
