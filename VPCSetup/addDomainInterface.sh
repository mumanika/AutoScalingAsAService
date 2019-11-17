#!/bin/bash

# Desc: Attach a new interface to connect the VM to the bridge.
# Arguments: VM Name, Bridge name

if [ $# -ne 2 ];
then
	exit
fi

virsh attach-interface --domain $1 --type direct --source ${1}${2} --config --model virtio 
