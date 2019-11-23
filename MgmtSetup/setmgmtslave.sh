#!/bin/bash


#Description: This script will set up a management network and create a VXLAN connection between the two sites. 
#Inputs: ip address of mgmt interface, ip address of slave manangement interface, ip address of ens4 remote site

if [ $# -ne 3 ]; 
then 
	echo "Invalid Arguments"
	exit
fi



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


