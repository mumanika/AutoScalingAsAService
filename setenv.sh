#!/bin/bash

#Set up the namespaces

ns_Input="NS1 10.10.10.0/24"
provider_ip=172.16.12.12/24
provider_nei_ip=172.16.12.13/24

i=$(echo $ns_Input | cut -d ' ' -f 2 | cut -d '.' -f 1-3)
ip=$(echo $ns_Input | cut -d ' ' -f 1)


ip netns del $i
ip netns add $i
ip netns exec $i brctl addbr $i'_br'
ip netns exec $i ip link set $i'_br' up
ip link add v$i type veth peer name 'v_'$i
ip link set 'v'$i netns $i
ip link set 'v_'$i netns Provider
ip netns exec $i ip link set 'v'$i up
ip netns exec $i ip addr add $ip'.1/24' dev 'v'$i
ip netns exec Provider ip link set 'v_'$i up 
ip netns exec Provider ip addr add $ip'.2/24' dev 'v_'$i
ip netns exec $i ip route add default via $ip'.2/24'









	

