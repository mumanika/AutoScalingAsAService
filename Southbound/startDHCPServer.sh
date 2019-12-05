#!/bin/bash

# Args: interface to listen for the DHCP server, lower bound of IP addresses for the subnet, upper bound for IP address for subnet, path to DHCP hostsfile (if using static IPs), Path to DNSMASQ config file

dnsmasq --interface=${1} --strict-order --dhcp-range=$2,$3 --bind-dynamic --dhcp-authoritative --dhcp-hostsfile=${4} --conf-file=${5} --dhcp-lease-max=253
