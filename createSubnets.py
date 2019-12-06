# creating subnets in both the sites for a tenant. Called in automate.yml

import json
import os
import sys
import subprocess
import shlex

inp_file = sys.argv[1]
flag = int(sys.argv[2])

def get_ip(address,last_idx):
    sub = address.split('.')
    ip=''
    for n,p in enumerate(sub):
        if n!= len(sub)-1:
            ip = ip+p+'.'
    ip = ip + str(last_idx)
    return ip


with open(inp_file,'r') as f:
    schema = json.load(f)

i=0

if flag == 0:
    for k in schema['subnet_list1']:
        first_ip_range = get_ip(k['subnet'],10)
        last_ip_range = get_ip(k['subnet'],240)
        subnet_name = k['name']
        subprocess.call(shlex.split('./addTenantSubnet.sh '+subnet_name+' '+schema['ns_name']+' '+k['subnet']+' '+str(k['prefix'])+' '+first_ip_range+' '+last_ip_range+' '+k['base_ns_subnet']))
        #for x in schema['subnet_list2']:
        #    if i+1 == x['id']:
        #        subprocess.call(shlex.split('./addRouteToSubnet.sh ' +schema['ns_name'] +' '+x['subnet']+'/'+x['prefix']+' ' +schema['gre_name']))
    i = i+1

    for x in schema['subnet_list2']:
        subprocess.call(shlex.split('./addRouteToSubnet.sh ' +schema['ns_name'] +' '+'71.71.71.71'+' ' +schema['gre_name']))
        subprocess.call(shlex.split('./addRouteToSubnet.sh ' +schema['ns_name'] +' '+x['base_ns_subnet']+'/'+str(x['prefix'])+' ' +schema['gre_name']))


else:
    i =0
    for k in schema['subnet_list2']:
            first_ip_range = get_ip(k['subnet'],10)
            last_ip_range = get_ip(k['subnet'],240)
            subnet_name = k['name']
            subprocess.call(shlex.split('/home/ece792/AutoScalingAsAService/addTenantSubnet.sh '+subnet_name+' '+schema['ns_name']+' '+k['subnet']+' '+str(k['prefix'])+' '+first_ip_range+' '+last_ip_range+' '+k['base_ns_subnet']))
            #for x in schema['subnet_list1']:
            #    if i+1 == x['id']:
            #        subprocess.call(shlex.split('/home/ece792/Project2/addRouteToSubnet.sh ' +schema['ns_name'] +' '+x['subnet']+'/'+x['prefix']+' ' +schema['gre_name']))
    i = i+1

    for x in schema['subnet_list1']:
         subprocess.call(shlex.split('/home/ece792/AutoScalingAsAService/addRouteToSubnet.sh ' +schema['ns_name'] +' '+'70.70.70.70'+' ' +schema['gre_name']))

         subprocess.call(shlex.split('/home/ece792/AutoScalingAsAService/addRouteToSubnet.sh ' +schema['ns_name'] +' '+x['base_ns_subnet']+'/'+str(x['prefix'])+' ' +schema['gre_name']))


#for k in schema['subnet_list'+str(flag+1)]:
#    first_ip_range = get_ip(k['subnet'],10)
#    last_ip_range = get_ip(k['subnet'],240)
#    subnet_name = k['name']
#    if flag ==0:
#        subprocess.call(shlex.split('./addTenantSubnet.sh '+schema['ns_name']+' '+str(i+1)+' '+k['subnet']+' '+k['prefix']+' '+first_ip_range+' '+last_ip_range+' '+subnet_name))
#        for x in schema['subnet_list2']:
#        subprocess.call(shlex.split('./addRouteToSubnet.sh ' +schema['ns_name'] +' '+k['subnet']+'/'+k['prefix']+' ' +schema['gre_name']))

#    else:
#        subprocess.call(shlex.split('/home/ece792/Project2/addTenantSubnet.sh '+schema['ns_name']+' '+str(i+1)+' '+k['subnet']+' '+k['prefix']+' '+first_ip_range+' '+last_ip_range+' '+subnet_name))
#        subprocess.call(shlex.split('/home/ece792/Project2/addRouteToSubnet.sh ' +schema['ns_name']+ ' '+ k['subnet']+'/'+k['prefix']+' '+schema['gre_name']))

#    i = i+1



