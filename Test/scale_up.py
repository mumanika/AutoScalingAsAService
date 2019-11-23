import subprocess
import time
import shlex
import libvirt
import sys
import json

file_name = sys.argv[1]
vm = sys.argv[2]
ns_name = sys.argv[3]
bridge_name = sys.argv[4]

file_name = '/home/ece792/Project2/'+file_name

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

subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'/home/ece792/Project2/create_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
subprocess.call(shlex.split('/home/ece792/Project2/addVMBridgeInterface.sh'+' '+ns_name+' '+bridge_name+' ' +vm))
subprocess.call(shlex.split('/home/ece792/Project2/addDomainInterface.sh'+' '+vm+' '+bridge_name))
subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'/home/ece792/Project2/start_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                #print(vm)
time.sleep(40)
#mac_address = get_mac(vm)
                ##subprocess.call(shlex.split('./addStaticIP.sh'+' '+mac_address+' '+vm+' '+vms['ip']+' '+NS_name+' '+h['subnet_name']))
ip_get = extract_ip(vm)

with open(file_name,'r') as f:
    schema = json.load(f)

for sub in schema['subnets']:
    for h in sub:
        if h['host'] == 'host2':
            h['vm_list'].append({'ip':ip_get,'name':vm,'id':int(h['vm_num'])+1})
            h['vm_num'] = str(int(h['vm_num'])+1)

        else:
            h['vm_num'] = str(int(h['vm_num'])+1)

schema['vm_list_lb'].append(ip_get)

with open(file_name,'w') as gg:
    json.dump(schema,gg,indent=4)


subprocess.call(shlex.split('sudo scp'+' ' + file_name+' '+' ece792@172.16.12.13:/home/ece792/Project/Test'))
    
