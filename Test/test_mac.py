
import libvirt

conn = libvirt.open('qemu:///system')






dom =conn.lookupByName("NS1v1")
mac=''
ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
for (name, val) in ifaces.iteritems():
    if name != "lo":
         mac =val['hwaddr']

print(mac)
