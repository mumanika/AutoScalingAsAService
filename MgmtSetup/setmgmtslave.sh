#!/bin/bash


#Description: This script will set up a management network and create a VXLAN connection between the two sites. 
#Inputs: ip address of mgmt interface, ip address of slave manangement interface, ip address of ens4 remote site, ip address of ens4 local site

if [ $# -ne 4 ]; 
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

ip link add name vxlan1 type vxlan id 100 local $4  remote $3 dstport 4789
ip link set vxlan1 up 
brctl addif mgmtbr vxlan1 

ip2=$(echo $2 | cut -d '.' -f 1-3)


