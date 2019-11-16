#!/bin/bash

# Desc: Sets up the L2 Bridge and attaches it to the namespace, the DNSMASQ configuration is done and the dhcp server runs at the namespace interface
# Arguments: namespace name, subnet number, subnet ID, prefix, first ip address in range, last ip in range, subnetName

if [ $# -ne 7 ];
then
	exit
fi

ip=$(echo $3 | cut -d '.' -f 1-3)

ip netns exec $1 brctl addbr ${1}'_br'${2}
ip netns exec $1 ip link set dev ${1}'_br'${2} up
ip netns exec $1 ip link add ${1}'_br'${2}NS type veth peer name NS${1}'_br'${2}
ip netns exec $1 brctl addif ${1}'_br'${2}NS
ip netns exec $1 ip link set ${1}'_br'${2}NS up
ip netns exec $1 ip addr add $ip'.1/'$4 dev NS${1}'_br'${2}
ip netns exec $1 ip link set NS${1}'_br'${2} up
dnsmasq --except-interface=lo --interface=NS${1}'_br'${2} --dhcp-range=$5,$6 --bind-interfaces --dhcp-authoritative --dhcp-hostsfile=/etc/${1}/${7}.hostsfile
