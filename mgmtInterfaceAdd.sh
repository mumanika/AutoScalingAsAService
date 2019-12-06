#!/bin/bash

# Desc: Attach a management interface to the specified VM. 
# Args: VM name

virsh attach-interface --domain $1 --type network --source mgmtNW --config --model virtio
