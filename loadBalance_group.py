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

public_ip =''

for x in schema['ns_ps subnet']:
    if x['host'] == 'host'+host_id:
        public_ip = x['ns_ps_subnet']

public_ip = get_ip(public_ip,2)


for grp in schema['scaling_groups']:
    for host in grp:
            if host['host'] == 'host'+host_id:
                if host_id == '1':
                    subprocess.call(shlex.split('./loadBalanceAddGroup.sh' +' '+host['name']+' '+ public_ip+' '+str(host['port'])+' '+schema['ns_name']))
                else:
                     subprocess.call(shlex.split('/home/ece792/AutoScalingAsAService/loadBalanceAddGroup.sh' +' '+host['name']+' '+ public_ip+' '+str(host['port'])+' '+schema['ns_name']))



