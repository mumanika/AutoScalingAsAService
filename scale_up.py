import json
import subprocess
import time
import shlex
import sys
import os
import random

def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip


file_name = sys.argv[1]
hyp_ip = sys.argv[2]
grp_name = sys.argv[3]

host_name =''

with open(file_name,'r') as f:
    schema = json.load(f)

with open('mgmt.json','r') as mgmt_f:
    mgmt_schema = json.load(mgmt_f)

for host in mgmt_schema['hosts']: #get host_name
    if host['mgmt_ip'] == hyp_ip:
        host_name = host['host']

grp_subnets = []

for grp in schema['scaling_groups']:
    for h in grp:
        if h['host'] == host_name:
            grp_subnets = h['members']

total_ct = schema['total_ct']
total_ct +=1
schema['total_ct'] = total_ct
grp_id= grp_name[1]

vm = 'C'+grp_id+'_'+total_ct

subnet_name = ''
rand_id = random.choice(grp_subnets)

for sub in schema['subnets']:
    flag =1
    for h in sub:
        if h['subnet_id'] ==  rand_id:
            subnet_name = h['subnet_name']
            flag =0
            break
    if flag == 0:
        break


#create_container
subprocess.call(shlex.split('sudo docker run -itd --name '+vm+' ece792 \'/bin/sh\''))
time.sleep(4)
pid = subprocess.check_output("sudo docker inspect -f '{{.State.Pid}}' "+vm, shell=True).strip()
subprocess.call(shlex.split('sudo ./addGuestBridgeInterface.sh '+subnet_name+ ' '+vm))
subprocess.call(shlex.split('sudo ./addContainerInterface.sh '+subnet_name+' '+vm+' '+pid))
os.system("sudo docker exec --privileged "+vm+" /etc/init.d/ssh start")

ip_get = subprocess.check_output("sudo docker container exec --privileged "+vm+" ip -4 addr show "+vm+subnet_name+"B | grep -oP \'(?<=inet\s)\d+(\.\d+){3}\'", shell=True).strip()

lb_base = false
base_ns_subnet = ''
idx =0

for sub in schema['subnets']:
    for h in sub:
        if h['host'] == host_name and subnet_name == h['subnet_name']:
            if len(h['container_list']) == 0:
                lb_base =true
            base_ns_subnet = h['base_ns_subnet']

            h['container_list'].append({
                "ip":ip_get,
                "name":vm
                })
            h['container_lb_list'].append(ip_get)
            idx = len(h['container_lb_list'])

if lb_base == true:
    n_packet = 0
    for sub in schema['subnets']:
        for h in sub:
            if h['subnet_id'] in grp_subnets:
                if len(h['container_list'] > 0:
                        n_packet +=1

    for host in mgmt_schema['hosts']:
        subprocess.call(shlex.split('ssh '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+' sudo /home/ece792/AutoScalingAsAService/loadBalanceBaseAdd.sh '+str(n_packet+1)+' '+get_ip(base_ns_subnet,2)+' 1025  '+schema['ns_name']+ ' ' +grp_name))


subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/loadBalanceAdd.sh '+str(idx)+' '+get_ip(base_ns_subnet,2)+' 1025 '+get_ip+' 22 '+ subnet_name))

with open(file_name,'w') as tt_f:
    json.dump(schema,tt_f,indent=4)


for host in mgmt_schema['hosts']:
    subprocess.call(shlex.split('sudo scp '+file_name+' ' +host['user']+'@'+host['mgmt_ip']+':/home/ece792/AutoScalingAsAService/'))



