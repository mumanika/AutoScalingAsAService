#!/bin/bash

# Desc: This script creates a new tenant namespace and connects it to the Provider. The default route is also given through the Provider. teh script also sets up the iptable rules for L3 isolation.
# Arguments: namspace name, Egress interface subnet (.2 is given to namespace and .1 is given to the provider),destination site address with mask, address to add to the loopback interface(with mask).

#####Argument format#######
# Namespace name <str>
# Egress Interface <ip> without the subnet is fine
# Destination interface of the tenant namespace <ip> 

# Eg. ./setNS.sh siteA 1.1.1.2 10.10.10.2 
#####Argument format#######


if [ $# -lt 3 ];
then
	exit
fi

ip=$(echo $2 | cut -d '.' -f 1-3)
src=$(echo $2 | cut -d '.' -f 1-3)
dst=$(echo $3 | cut -d '.' -f 1-3)


ip netns del $1
ip netns add $1
ip link add ${1}Prov type veth peer name Prov$1
ip link set ${1}Prov netns $1
ip link set Prov$1 netns Provider
ip netns exec $1 ip addr add $ip'.2/24' dev ${1}Prov
ip netns exec $1 ip link set ${1}Prov up
ip netns exec Provider ip addr add $ip'.1/24' dev Prov$1
ip netns exec Provider ip link set Prov$1 up
ip netns exec $1 ip route add default via $ip'.1'
if [ $# -gt 3];
then
	if [ $# -ne 4];
	then
		exit
	fi	
	ip netns exec $1 ip addr add $4 dev lo
fi
ip netns exec $1 ip link set lo up
ip netns exec $1 iptables -t nat -A POSTROUTING -o ${1}Prov -j MASQUERADE
#echo $src
ip netns exec Provider iptables -t filter -I FORWARD 1 -i vProv -o Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -o vProv -i Prov$1 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -s "${src}".0/24 -d "${dst}".0/24 -j ACCEPT
ip netns exec Provider iptables -t filter -I FORWARD 1 -d "${src}.0/24" -s "${dst}.0/24" -j ACCEPT


mkdir /etc/netns/
rm -rf /etc/netns/${1}/
mkdir /etc/netns/${1}/

echo "no-resolv" >> /etc/netns/${1}/dnsmasq.conf
echo "server=127.0.0.1" >> /etc/netns/${1}/dnsmasq.conf
echo "server=8.8.8.8" >> /etc/netns/${1}/dnsmasq.conf
echo "nameserver 127.0.0.1" >> /etc/netns/${1}/resolv.conf
