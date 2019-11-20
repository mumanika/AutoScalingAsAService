import subprocess
import ipaddress
import libvirt

def setupSubnetsFronJSON(subnetInfoDict, nsName):
    for i in subnetInfoDict:
        a = ipaddress.ip_network(i['IP']+'/'+i['prefix']);
        subprocess.check_output(['addTenantSubnet.sh',nsName+' '+i['count_of_subnets']+' '+i['IP']+' '+i['prefix']+' '+str(a[2])+' '+str(a[-2])+' '+i['name']]);
        k = 0;
        for j in i['VMs']:
            subprocess.check_output(['addVMBridgeInterface.sh',nsName+' '+i['bridge_name']+' '+j['name']]);
            subprocess.check_output(['addDomainInterface.sh',j['name']+' '+i['bridge_name']]);
            dom = conn.lookupByName(j['name']);
            ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0);
            if('IP' in j):
                for (name, val) in ifaces.iteritems():
                    if name != "lo":
                        subprocess.check_output(['addStaticIP.sh',val['hwaddr']+' '+j['name']+' '+str(a[2+k])+' '+nsName+' '+i['name']);

def deleteStaticIPEntry(vmName,nsName,subnetName):
    with open("yourfile.txt", "r") as f:
        lines = f.readlines()
    with open("yourfile.txt", "w") as f:
        for line in lines:
            if vmName not in line.strip('\n'):
                f.write(line);
