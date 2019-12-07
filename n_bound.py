import os
import subprocess
import shlex
import json
import time
from datetime import datetime

with open('tenant_count.json','r') as f:
    count_schema = json.load(f)

with open('input_T1.json','r') as ff:
    input_schema = json.load(ff)

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

def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip



t_ct = int(count_schema['count'])+1
ps_host1_subnet = count_schema['last_subnet_used'] #provide NS-PS ip
ps_host2_subnet = update(ps_host1_subnet)
tenant_name = "T"+str(t_ct)
starting_tenant_address = count_schema['last_tenant_used_subnet']  #provide NS-base -> tenant IP
temp_starting_tenant_address = starting_tenant_address

subnet_count = input_schema['subnet_count']
start_port = count_schema['port']
scaling_grp_ct = len(input_schema['scaling_groups'])


count_schema['count']=t_ct
count_schema['last_subnet_used'] = update(ps_host2_subnet)
for ct in range(0,2*int(subnet_count)):
    temp_starting_tenant_address = update(temp_starting_tenant_address)
count_schema['last_tenant_used_subnet'] = temp_starting_tenant_address
count_schema['port'] = start_port + scaling_grp_ct

#updated tenant_count.json file and written back. Used for next tenant
with open('tenant_count.json','w') as w_f:
    json.dump(count_schema,w_f,indent=4)


subnet_list=[]
host2_subnet_list=[]
prefix_list=[]
base_ns_subnet_list=[]
host2_base_ns_subnet_list=[]

tenant ={} #need to be uploaded in tenant_name.json file
tenant['subnet_num'] = subnet_count
NS_name = "NS"+str(t_ct)
tenant['ns_name'] = NS_name
tenant['ns_ps subnet'] = []
tenant['ns_ps subnet'].append({'host':'host1','ns_ps_subnet':ps_host1_subnet,'ns_ps_prefix':24})
tenant['ns_ps subnet'].append({'host':'host2','ns_ps_subnet':ps_host2_subnet,'ns_ps_prefix':24})
tenant['subnets'] = []

temp_container_count = 0
temp = 0

for sub in input_schema['subnets']:
    subnet_address = sub['address']
    subnet_list.append(subnet_address)
    
    prefix = sub['prefix']
    prefix_list.append(sub['prefix'])

    container_ct = sub['container_ct']
    container_name_list =[]
    container_ip_list =[]

    for i in range(0,int(container_ct)):
            container_name = "C"+str(t_ct)+"_"+str(temp_container_count+1)
            container_name_list.append(container_name)
            #container_ip = get_ip(subnet_address,i+2)
            container_ip = ' '
            container_ip_list.append(container_ip)
            temp_container_count +=1
    
    container_list =[]
    for i in range(0,int(container_ct)):
        container_list.append({ 'name': container_name_list[i], 'ip': container_ip_list[i] })

    #need to see bridge_name

    #if sub['policy'] == 'dynamic':
    #    policy = {}
    #    policy['type']='dynamic'
    #    policy['max_cpu'] = sub['max_cpu']
    #    policy['max_mem'] = sub['max_memory']
    #    policy['min_cpu'] = sub['min_cpu']
    #    policy['min_mem'] = sub['min_memory']

    #else:
    #    policy ={}
    #    policy['type']='static'
    #    policy['time'] = sub['time']
    
    base_ns_subnet = starting_tenant_address
    base_ns_subnet_list.append(base_ns_subnet)
    starting_tenant_address = update(starting_tenant_address)
    print(starting_tenant_address)

    hosts =[]

    hosts.append({
            'subnet_name':tenant_name+'S'+str(temp+1),
            'host':'host1',
            'subnet_id':temp+1,
            'subnet_address' : subnet_address,
            'prefix':prefix,
            'base_ns_subnet':base_ns_subnet,
            'container_ct' : container_ct,
            'container_list' : container_list,
            'container_lb_list':[],
            'scale_up_flag' :'0',
            'bridge':tenant_name+'S'+str(temp+1)+'B'
            })

    host2_subnet_address = update(subnet_address)
    host2_subnet_list.append(host2_subnet_address)
    host2_container_list =[]
    host2_base_ns_subnet = starting_tenant_address
    host2_base_ns_subnet_list.append(host2_base_ns_subnet)
    starting_tenant_address = update(starting_tenant_address)


    hosts.append({
            'subnet_name':tenant_name+'S'+str(temp+1),
            'host':'host2',
            'subnet_id':temp+1,
            'subnet_address' : host2_subnet_address,
            'prefix':prefix,
            'base_ns_subnet':host2_base_ns_subnet,
            'container_ct' : container_ct,
            'container_list' : host2_container_list,
            'container_lb_list':[],
            'scale_up_flag' :'0',
            'bridge':tenant_name+'S'+str(temp+1)+'B'
            })
    
    tenant['subnets'].append(hosts)
    temp = temp+1

tenant['total_ct'] = temp_container_count #used to assign container names easily
tenant['lo_h1'] = '70.70.70.70'
tenant['lo_h2'] = '71.71.71.71'
tenant['scaling_groups'] =[]
t_idx =0
for k in input_schema['scaling_groups']:
    member_list = k["members"]
    grp_subnet_list = []
    grp_base_ns_subnet_list =[]
    host2_grp_subnet_list =[]
    host2_grp_base_ns_subnet_list =[]

    for mem in member_list:
        grp_subnet_list.append(subnet_list[mem-1])
        grp_base_ns_subnet_list.append(base_ns_subnet_list[mem-1])
        host2_grp_subnet_list.append(host2_subnet_list[mem-1])
        host2_grp_base_ns_subnet_list.append(host2_base_ns_subnet_list[mem-1])

    if k['policy'] == 'dynamic':
        policy = {}
        policy['type']='dynamic'
        policy['max_cpu'] = k['max_cpu']
        policy['max_mem'] = k['max_memory']
        policy['min_cpu'] = k['min_cpu']
        policy['min_cont'] = k['min_container']

    else:
        policy ={}
        policy['type']='static'
        policy['weekday'] = k['weekday']
        policy['number']=k['number']

    hosts=[]
    hosts.append({
        'host':'host1',
        'members':member_list,
        'port':start_port,
        'name':'G'+str(t_idx+1),
        'subnet_list':grp_subnet_list,
        'base_ns_subnet_list':grp_base_ns_subnet_list,
        'policy':policy
        })

    hosts.append({
        'host':'host2',
        'members':member_list,
        'port':start_port,
        'name':'G'+str(t_idx+1),
        'subnet_list':host2_grp_subnet_list,
        'base_ns_subnet_list':host2_grp_base_ns_subnet_list,
        'policy':policy
        })



    tenant['scaling_groups'].append(hosts)
    start_port +=1
    t_idx +=1

tenant['scaling_metadata']=[]
idx =0
for k in input_schema['scaling_groups']:
    dic ={}
    dic['name'] = 'G'+str(idx+1)
    dic['flag'] = 1
    dic['timer'] = str(datetime.now())
    tenant['scaling_metadata'].append(dic)
    idx +=1

tenant['cooldown'] = 2
tenant['log_file'] = "log_"+tenant_name+".txt"

log_f = open("log_"+tenant_name+".txt","a+")

file_name = tenant_name+".json"
with open(file_name,'w') as outfile:
    json.dump(tenant,outfile,indent=4)

#callling older file itself

local_ip = get_ip(ps_host1_subnet,2)
remote_ip = get_ip(ps_host2_subnet,2)


arg_vars={}
arg_vars['ns_name']= NS_name
arg_vars['gre_name']=NS_name+"_gre"
arg_vars['subnet_count']=int(subnet_count)
arg_vars['setNS1']={'local_ps':ps_host1_subnet,'remote_ps':ps_host2_subnet,'lo':'70.70.70.70'}
arg_vars['setNS2']={'local_ps':ps_host2_subnet,'remote_ps':ps_host1_subnet,'lo':'71.71.71.71'}

arg_vars['addGre1']={'local_ip':local_ip,'remote_ip':remote_ip,'n_hop':'99.99.99.1','next_hop':'172.16.12.12'}
arg_vars['addGre2']={'local_ip':remote_ip,'remote_ip':local_ip,'n_hop':'100.100.100.1','next_hop':'172.16.12.13'}

arg_vars['subnet_list1'] = []
for i in range(0,int(subnet_count)):
    s_name = tenant_name +"S"+ str(i+1)
    arg_vars['subnet_list1'].append({'subnet':subnet_list[i],'prefix':prefix_list[i],'name':s_name,'id':i,'base_ns_subnet':base_ns_subnet_list[i]})

arg_vars['subnet_list2'] = []
for i in range(0,int(subnet_count)):
    s_name = tenant_name +"S"+ str(i+1)
    arg_vars['subnet_list2'].append({'subnet':host2_subnet_list[i],'prefix':prefix_list[i],'name':s_name,'id':i,'base_ns_subnet':host2_base_ns_subnet_list[i]})


arg_vars['json'] = file_name

arg_file = file_name.split('.')[0]+"_vars.json"
with open(arg_file,'w') as ofile:
    json.dump(arg_vars,ofile,indent=4)

subprocess.call(shlex.split('sudo scp'+' ' + arg_file+' '+' ece792@172.16.12.12:/home/ece792/AutoScalingAsAService'))
subprocess.call(shlex.split('sudo scp'+' ' +file_name+' '+' ece792@172.16.12.12:/home/ece792/AutoScalingAsAService'))
#subprocess.call(shlex.split('sudo scp'+' ' +'addRouteToSubnet.sh'+' '+' ece792@172.16.12.12:/home/ece792/Project2'))

#call automation
subprocess.call(shlex.split('sudo'+' '+'ansible-playbook'+' '+'automate.yml'+ ' '+'-i' +' ' +'./inventory'+' '+'--extra-var'+ ' '+'inp_file='+arg_file))

#add lb for each machine 

with open(file_name,'r') as lb_f:
    lb_schema = json.load(lb_f)

for sub in lb_schema['subnets']:
    for h in sub:
        if h['host'] == 'host1':
            lb_list = h['container_lb_list']
            for num,ip in enumerate(lb_list):
                subprocess.call(shlex.split('sudo ./loadBalanceAdd.sh '+str(num+1)+' '+get_ip(h['base_ns_subnet'],2)+' 1025 '+ip+' 22 '+h['subnet_name']))



#call cron job here for monitoring
#subprocess.call(shlex.split('sudo python'+' '+'startCron.py'+' '+file_name))











