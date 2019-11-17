import json

with open('T2.json','r') as f:
    schema = json.load(f)

print schema['subnet_num']

for k in schema['subnets']:
    for i in k:
        if i['host'] == 'host1':
            print i['vm_list']
