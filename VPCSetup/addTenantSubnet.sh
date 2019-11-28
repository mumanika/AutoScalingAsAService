#!/bin/bash

# Desc: Sets up a new namespace with an L2 Bridge, the DNSMASQ configuration is done and the dhcp server runs at the subnet namespace interface. Then connect this subnet namespace to the tenant's base namespace. These subnets are able to support north-south as well as east-west traffic.
# Arguments: subnet namespace name, tenant base namespace name, subnet IP address, prefix, first ip address in range, last ip in range, the subnet ip address of the connection between subnet namespace and base namespace

if [ $# -ne 7 ];
then
	exit
fi

ip=$(echo $3 | cut -d '.' -f 1-3)
ip2=$(echo $7 | cut -d '.' -f 1-3)

ip netns del $1
ip netns add $1
ip netns exec $1 ip link add ${1}Bse type veth pee name Bse${1}
ip netns exec $1 ip link set dev Bse${1} netns ${2}
ip netns exec $1 ip addr add ${ip2}'.2/24' dev ${1}Bse
ip netns exec $1 ip link set dev ${1}Bse up
ip netns exec $2 ip addr add ${ip2}'.1/24' dev Bse${1}
ip netns exec $2 ip link set dev Bse${1} up
ip netns exec $1 brctl addbr ${1}'B'
ip netns exec $1 ip link set dev ${1}'B' up
ip netns exec $1 ip link add ${1}'B'NS type veth peer name NS${1}'B'
ip netns exec $1 brctl addif ${1}'B' ${1}'B'NS
ip netns exec $1 ip link set ${1}'B'NS up
ip netns exec $1 ip addr add $ip'.1/'$4 dev NS${1}'B'
ip netns exec $1 ip link set NS${1}'B' up
ip netns exec $1 rm -f /etc/${1}.hostsfile
ip netns exec $1 rm -f /etc/netns/${1}/${1}.hostsfile
ip netns exec $1 touch /etc/${1}.hostsfile
ip netns exec $1 touch /etc/netns/${1}/${1}.hostsfile
ip netns exec $1 dnsmasq --interface=NS${1}'B' --strict-order --dhcp-range=$5,$6 --bind-dynamic --dhcp-authoritative --dhcp-hostsfile=/etc/netns/${1}/${1}.hostsfile --conf-file=/etc/netns/${1}/dnsmasq.conf --dhcp-lease-max=253
