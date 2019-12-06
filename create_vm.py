import libvirt
import sys
import json
import subprocess
import shlex
import time

f_name = sys.argv[1]

def get_mac(vm):
    conn = libvirt.open('qemu:///system')
    print vm
    dom =conn.lookupByName(vm)
    while(True):
        if(dom.isActive() == 1):
           break

    mac=''
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    for (name, val) in ifaces.iteritems():
        if name != "lo":
            mac =val['hwaddr']
    return mac

def extract_ip(vm):
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(vm)
    ip=' '
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    for (name,val) in ifaces.iteritems():
        if name !="lo":
             if val['addrs']:
                for ipaddr in val ['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        ip = ipaddr['addr']
    return ip




with open(f_name,'r') as f:
    sc = json.load(f)

schema_file = sc['json']

with open(schema_file,'r') as g:
    schema = json.load(g)

for k in schema['subnets']:
    for h in k:
        if h['host'] == 'host1':
            for vms in h['container_list']:
                vm = vms['name']
                subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'create_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                subprocess.call(shlex.split('./addVMBridgeInterface.sh '+h['subnet_name']+' '+vm))
                subprocess.call(shlex.split('./addDomainInterface.sh'+' '+vm+' '+h['subnet_name']))
                subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'start_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                #print(vm)
                time.sleep(40)
                mac_address = get_mac(vm)
                ##subprocess.call(shlex.split('./addStaticIP.sh'+' '+mac_address+' '+vm+' '+vms['ip']+' '+NS_name+' '+h['subnet_name']))
                ip_get = extract_ip(vm)
                vms['ip'] = ip_get
                h['container_lb_list'].append(ip_get)

with open(schema_file,'w') as tt_f:
    json.dump(schema,tt_f,indent=4)

