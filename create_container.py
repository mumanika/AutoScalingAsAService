import json
import subprocess
import shlex
import sys
import time
import os
import pexpect

f_name = sys.argv[1]

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
                subprocess.call(shlex.split('sudo docker run -itd --name '+vm+' ece792 \'/bin/bash\''))
                time.sleep(4)
                pid = subprocess.check_output("sudo docker inspect -f '{{.State.Pid}}' "+vm, shell=True).strip()
                subprocess.call(shlex.split('sudo ./addGuestBridgeInterface.sh '+h['subnet_name']+ ' '+vm))
                subprocess.call(shlex.split('sudo ./addContainerInterface.sh '+h['subnet_name']+' '+vm+' '+pid))


                #subprocess.call(shlex.split('sudo docker exec --privileged '+vm+' service ssh start'))
                
                #os.system("sudo docker exec "+vm+" /etc/init.d/ssh stop")
                os.system("sudo docker exec --privileged "+vm+" /etc/init.d/ssh start")



                ip_get = subprocess.check_output("sudo docker container exec --privileged "+vm+" ip -4 addr show "+vm+h['subnet_name']+"B | grep -oP \'(?<=inet\s)\d+(\.\d+){3}\'", shell=True).strip()
                vms['ip'] = ip_get
                h['container_lb_list'].append(ip_get)


with open(schema_file,'w') as tt_f:
    json.dump(schema,tt_f,indent=4)

    


