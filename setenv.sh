#!/bin/bash

#Set up the namespaces

ip=$(echo $2 | cut -d '.' -f 1-3)
i=$1


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
ip netns exec $i ip route add default via $ip'.2'









	

