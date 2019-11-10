#!/bin/bash

#set up the provider namespace

#$1 is provider ip and $2 is neighbout ip /24format

provider_ip=$1
provider_nei_ip=$2

ip netns del Provider
ip netns add Provider
ip link set ens4 netns Provider
ip netns exec Provider ip link set ens4 up
ip addr add $provider_ip dev ens4
ip route add default via $provider_nei_ip