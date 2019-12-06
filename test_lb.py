import json
import subprocess
import shlex

# load balancing scripts to be called

#create new chain per group

with open(file_name,'r') as new_f:
    new_schema = json.load(new_f)

base_ns_subnet_list = ['100.0.1.0


for k in new_schema['scaling_groups']:
    subprocess.call(shlex.split('./loadBalanceAddGroup.sh'+' '+k['name']+' '+'3.3.1.2'+' '+k['port']+' '+'NS1'))

#call load balance per base
for k in new_schema['scaling_groups']:



