#!/bin/bash

# Desc: Get the IPv4 address of the conatiner interface attached to a subnet.
# Args: container name, subnet namespace name

docker container exec ${1} ip -4 addr show ${1}${2}'B' | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
