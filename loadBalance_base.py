import json
import subprocess
import shlex
import sys


file_name = sys.argv[1]
host_id = sys.argv[2]

def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip

with open(file_name,'r') as f:
    schema = json.load(f)

def get_count(mem,h_name,schema):
    for sub in schema['subnets']:
        for h in sub:
            if h['host'] == h_name and h['subnet_id']==mem:
                return len(h['container_list'])


for grp in schema['scaling_groups']:
    idx =0
    for host in grp:
        lo=''
        temp =0
        h_name = host['host']
        mem_list = host['members']

        for mem in mem_list:
            num = get_count(mem,h_name,schema)
            if num > 0:
                if host_id == '1':
                    subprocess.call(shlex.split('./loadBalanceBaseAdd.sh' +' '+str(idx+1)+' '+get_ip(host['base_ns_subnet_list'][temp],2)+' '+ '1025'+' '+schema['ns_name']+ ' '+host['name']))
                else:
                     subprocess.call(shlex.split('/home/ece792/Project2/Finaltest/loadBalanceBaseAdd.sh' +' '+str(idx+1)+' '+get_ip(host['base_ns_subnet_list'][temp],2)+' '+ '1025'+' '+schema['ns_name']+ ' '+host['name']))

                idx +=1
            temp +=1

