import os
import subprocess
import json


#tenant enter details
with open('tenant_count.json','r') as f:
    sc = json.load(f)

with open('tenant_details.json','r') as g:
    schema = json.load(g)

print("Enter the subnet address:")
subnet = raw_input()
print("Enter the Number of VM's you want to spawn")
vm_num = raw_input()

vm_name_list=[]
for i in range(0,int(vm_num)):
    print("Enter the VM Name")
    vm_name = raw_input()
    vm_name_list.append(vm_name)


print("Enter the maximum cpu threshold:")
cpu_threshold = raw_input()

print("Enter the maximum memory threshold:")
mem_threshold = raw_input()

ct = int(sc['count'])+1
tenant_name = "T"+str(ct)

sc['count'] = ct
with open('tenant_count.json','w') as j:
    json.dump(sc,j,indent =4)

tenant ={}
tenant['name'] = tenant_name
tenant['subnet'] = subnet
tenant['vm_num'] = vm_num
tenant['vm_list'] = []
for i in range(0,int(vm_num)):
    mgmt_details = []
    tenant['vm_list'].append({'name':vm_name_list[i],'mgmt':mgmt_details})

tenant['cpu_threshold'] = cpu_threshold
tenant['mem_threshold'] = mem_threshold

if 'tenant_list' not in schema:
    schema['tenant_list'] = []

schema['tenant_list'].append(tenant)

with open('tenant_details.json','w') as jj:
    json.dump(schema,jj,indent=4)

#Need to spawn the VM'S here call scaleup script


