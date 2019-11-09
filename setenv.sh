#!/bin/bash

#Set up the namespaces

ns_Input="NS1 NS2"


ip netns del Provider
ip netns add Provider
ip link add vProvider type veth peer name v_Provider
ip link set v_Provider up
ip addr add 99.99.99.2/24 dev v_Provider
ip link set vProvider netns Provider
ip netns exec Provider ip addr add 99.99.99.1/24 dev vProvider
ip netns exec Provider ip link set vProvider up
ip route add 99.99.99.0/24 dev v_Provider

for i in $ns_Input
do
	ip netns del $i
	ip netns add $i
	ip netns exec $i brctl addbr $i'_br'
	ip netns exec $i ip link set $i'_br' up
	ip link add v$i type veth peer name 'v_'$i
	ip link set 'v'$i netns $i
	ip link set 'v_'$i netns Provider
	ip netns exec $i ip link set 'v'$i up
	ip netns exec $i ip addr add "${i//[!0-9]/}.${i//[!0-9]/}.${i//[!0-9]/}"'.1/24' dev 'v'$i
	ip netns exec $i ip route add default dev 'v'$i
	ip netns exec Provider ip link set 'v_'$i up 
	ip netns exec Provider ip addr add "${i//[!0-9]/}.${i//[!0-9]/}.${i//[!0-9]/}".'2/24' dev 'v_'$i
done




	

