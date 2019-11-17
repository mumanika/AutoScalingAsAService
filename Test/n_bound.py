import os
import subprocess
import json
import shlex

with open('tenant_count.json','r') as f:
    t_count = json.load(f)

with open('tenant_list.json','r') as g:
    t_list = json.load(g)

def update(address):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n == len(sub)-2:
            x = int(p)+1
            ip = ip+str(x)+'.'
        else:
            ip = ip+p+'.'
    ip = ip[:-1]
    return ip

ct = int(t_count['count'])+1
ps_host1_subnet = t_count['last_subnet_used'] #provide NS-PS ip
ps_host2_subnet = update(ps_host1_subnet)
tenant_name = "T"+str(ct)
t_count['count']= ct
t_count['last_subnet_used'] = update(ps_host2_subnet)

with open('tenant_count.json','w') as t_count_1:
    json.dump(t_count,t_count_1,indent=4)

file_name = tenant_name+".json" #Eg:t1.json
t_list[tenant_name] = file_name

with open('tenant_list.json','w') as t_list_2:
    json.dump(t_list,t_list_2,indent=4)


def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip

#take the tenant input details

print("Enter the number of subnets:")
subnet_count = raw_input()
subnet_list=[]
prefix_list=[]
temp = 0 

tenant ={} #need to be uploaded in t_name.json file
tenant['subnet_num'] = subnet_count
NS_name = "NS"+str(ct)
tenant['ns_name'] = "NS"+str(ct)
tenant['ns_ps subnet'] = []
tenant['ns_ps subnet'].append({'host':'host1','ns_ps_subnet':ps_host1_subnet,'ns_ps_prefix':24})
tenant['ns_ps subnet'].append({'host':'host2','ns_ps_subnet':ps_host2_subnet,'ns_ps_prefix':24})
tenant['subnets'] = []

for temp in range(0,int(subnet_count)):
        print("New Subnet details:")
        print("Enter the subnet address")
        subnet_address = raw_input()
        subnet_list.append(subnet_address)

        print("Enter the prefix/mask:")
        prefix = raw_input()
        prefix_list.append(prefix)

        print("Enter the number of VM's you want:")
        vm_num = raw_input()

        vm_name_list =[]
        vm_ip_list =[]

        for i in range(0,int(vm_num)):
            print("Enter the vm_name:")
            vm_name = raw_input()
            vm_name = NS_name+"S"+str(temp+1)+vm_name
            vm_name_list.append(vm_name)
            vm_ip = get_ip(subnet_address,i+2)
            vm_ip_list.append(vm_ip)
        
        print("Enter the maximum CPU threshold:")
        cpu_threshold = raw_input()

        print("Enter the maximum memory threshold:")
        mem_threshold = raw_input()
        
        bridge_name = "NS"+str(ct)+"_br"+str(temp+1)
        NS_ip = get_ip(subnet_address,1)
        
        vm_list =[]
        for i in range(0,int(vm_num)):
            vm_list.append({ 'name': vm_name_list[i], 'ip': vm_ip_list[i] } )
        
        hosts =[]

        hosts.append({
            'host':'host1',
            'subnet_id':temp+1,
            'subnet_address' : subnet_address,
            'prefix':prefix,
            'vm_num' : vm_num,
            'vm_list' : vm_list,
            'bridge': bridge_name,
            'ns_ip' : NS_ip,
            'cpu_threshold' : cpu_threshold,
            'mem_threshold' : mem_threshold,
            'scale_up_flag' :'0'
            })
       
        host2_subnet_address = update(subnet_address)
        host2_vm_list =[]
        host2_NS_ip = get_ip(host2_subnet_address,1)
        hosts.append({
           'host':'host2',
           'subnet_id':temp+1,
           'subnet_address':host2_subnet_address,
           'prefix':prefix,
           'vm_num':0,
           'vm_list': host2_vm_list,
           'bridge':bridge_name,
           'ns_ip':host2_NS_ip,
           'cpu_threshold': cpu_threshold,
           'mem_threshold': mem_threshold,
           })
        tenant['subnets'].append(hosts)
                 

        
with open(file_name,'w') as outfile:
    json.dump(tenant,outfile,indent=4)


subprocess.call(shlex.split('./setNS.sh '+NS_name+' '+ps_host1_subnet+' '+ps_host2_subnet))
gre_name = NS_name+"_gre"
local_ip = get_ip(ps_host1_subnet,2)
remote_ip = get_ip(ps_host2_subnet,2)
next_hop = '172.16.12.12'

subprocess.call(shlex.split('./addTenantGRETunnel.sh '+NS_name+' ' +gre_name+' '+local_ip+' '+remote_ip+' '+ next_hop))

for i in range(0,int(subnet_count)):
    first_ip_range = get_ip(subnet_list[i],10)
    last_ip_range = get_ip(subnet_list[i],240)
    subnet_name = tenant_name + "S"+str(i+1)
    subprocess.call(shlex.split('./addTenantSubnet.sh '+NS_name+' '+str(i+1)+' '+subnet_list[i]+' '+prefix_list[i]+' '+first_ip_range+' '+last_ip_range+' '+subnet_name))

with open(file_name,'r') as t_f:
    schema = json.load(t_f)


for k in schema['subnets']:
    for h in k:
        if h['host'] == 'host1':
            for vm in h['vm_list']:
                subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'create_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                subprocess.call(shlex.split('./addVMBridgeInterface.sh'+' '+NS_name+' '+h['bridge']+' ' +vm))
                subprocess.call(shlex.split('./addDomainInterface.sh'+' '+vm+' '+h['bridge']))




    
        
        

