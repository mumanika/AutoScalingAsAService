import json

with open('T1.json','r') as f:
    schema = json.load(f)

print schema['subnet_num']

for k in schema['subnets']:
    for i in k:
        if i['host'] == 'host1':
            for vm in i['vm_list']:
                vm_name = vm['name']
                print vm_name
                print vm['ip']
