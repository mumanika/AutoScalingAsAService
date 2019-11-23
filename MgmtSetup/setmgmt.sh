#!/bin/bash


#Description: This script will set up a management network and create a VXLAN connection between the two sites. 
#Inputs: ip address of mgmt interface, ip address of slave manangement interface, ip address of ens4 remote site

if [ $# -ne 3 ]; 
then 
	echo "Invalid Arguments"
	exit
fi

mkdir /etc/mgmtDir
touch /etc/mgmtDir/dnsmasq.conf
echo "no-resolv" >> /etc/mgmtDir/dnsmasq.conf
echo "server=127.0.0.53" >> /etc/mgmtDir/dnsmasq.conf
echo "server=8.8.8.8" >> /etc/mgmtDir/dnsmasq.conf


brctl addbr mgmtbr
ip link set mgmtbr up
virsh net-define /root/AutoScalingAsAService/MgmtSetup/mgmtnw.xml
virsh net-start mgmtnet

ip link add mgmtbrhost type veth peer name hostmgmtbr
ip link set mgmtbrhost up
ip link set hostmgmtbr up 

brctl addif mgmtbr mgmtbrhost

ip=$(echo $1 | cut -d '.' -f 1-3)
ip addr add $1/24 dev hostmgmtbr 

ip link add name vxlan1 type vxlan id 100 dev hostmgmtbr remote $2 dstport 4789
ip link set vxlan1 up 
brctl addif mgmtbr vxlan1 

ip2=$(echo $2 | cut -d '.' -f 1-3)
ip route add $ip2.0/24 via $3 

dnsmasq --interface=NS${1}'B'${2} --strict-order --dhcp-range=$ip.3,$ip.254 --bind-dynamic --dhcp-authoritative  --conf-file=/etc/mgmtDir/dnsmasq.conf --dhcp-lease-max=253

#dnsmasq --interface=NS${1}'B'${2} --strict-order --dhcp-range=$5,$6 --bind-dynamic --dhcp-authoritative --dhcp-hostsfile=/etc/netns/${1}/${7}.hostsfile --conf-file=/etc/netns/${1}/dnsmasq.conf --dhcp-lease-max=253
