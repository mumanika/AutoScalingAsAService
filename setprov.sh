#!/bin/bash

#set up the provider namespace

provider_ip=172.16.12.12/24
provider_nei_ip=172.16.12.13/24
ip netns del Provider
ip netns add Provider
ip link set ens4 netns Provider
ip netns exec Provider ip link set ens4 up
ip addr add $provider_ip dev ens4
ip route add default via $provider_nei_ip