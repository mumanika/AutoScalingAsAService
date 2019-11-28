#!/bin/bash

# Desc: Attach a new interface to connect the VM to the bridge.
# Arguments: VM Name, subnet namespace name

if [ $# -ne 2 ];
then
	exit
fi

arg=$(echo ${2}'B')
virsh attach-interface --domain $1 --type direct --source ${1}${arg} --config --model virtio 
