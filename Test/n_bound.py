import os
import subprocess
import json
import shlex
import libvirt
import time





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
host2_subnet_list=[]
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
            vm_name = NS_name+"V"+str(i+1)
            vm_name_list.append(vm_name)
            vm_ip = ' '
            vm_ip_list.append(vm_ip)
        
        print("Enter the maximum CPU threshold:")
        cpu_threshold = raw_input()

        print("Enter the maximum memory threshold:")
        mem_threshold = raw_input()
        
        bridge_name = "NS"+str(ct)+"B"+str(temp+1)
        NS_ip = get_ip(subnet_address,1)
        
        vm_list =[]
        for i in range(0,int(vm_num)):
            vm_list.append({ 'name': vm_name_list[i], 'ip': vm_ip_list[i],'id':str(i+1) } )
        
        hosts =[]

        hosts.append({
            'subnet_name':tenant_name+'S'+str(temp+1),
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
            'scale_up_flag' :'0',
            'lo': '70.70.70.70'
            })
       
        host2_subnet_address = update(subnet_address)
        host2_subnet_list.append(host2_subnet_address)
        host2_vm_list =[]
        host2_NS_ip = get_ip(host2_subnet_address,1)
        hosts.append({
           'subnet_name':tenant_name+'S'+str(temp+1),
           'host':'host2',
           'subnet_id':temp+1,
           'subnet_address':host2_subnet_address,
           'prefix':prefix,
           'vm_num':vm_num,
           'vm_list': host2_vm_list,
           'bridge':bridge_name,
           'ns_ip':host2_NS_ip,
           'cpu_threshold': cpu_threshold,
           'mem_threshold': mem_threshold,
           'lo' :'71.71.71.71'
           })
        tenant['subnets'].append(hosts)
                 

        
with open(file_name,'w') as outfile:
    json.dump(tenant,outfile,indent=4)

local_ip = get_ip(ps_host1_subnet,2)
remote_ip = get_ip(ps_host2_subnet,2)

#creating arg_file.json for ansible script
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
    arg_vars['subnet_list1'].append({'subnet':subnet_list[i],'prefix':prefix_list[i],'name':s_name,'id':i})

arg_vars['subnet_list2'] = []
for i in range(0,int(subnet_count)):
    s_name = tenant_name +"S"+ str(i+1)
    arg_vars['subnet_list2'].append({'subnet':host2_subnet_list[i],'prefix':prefix_list[i],'name':s_name,'id':i})


arg_vars['json'] = file_name

arg_file = file_name.split('.')[0]+"_vars.json"
with open(arg_file,'w') as ofile:
    json.dump(arg_vars,ofile,indent=4)

subprocess.call(shlex.split('sudo scp'+' ' + arg_file+' '+' ece792@172.16.12.12:/home/ece792/Project2'))
subprocess.call(shlex.split('sudo scp'+' ' +file_name+' '+' ece792@172.16.12.12:/home/ece792/Project2'))
#subprocess.call(shlex.split('sudo scp'+' ' +'addRouteToSubnet.sh'+' '+' ece792@172.16.12.12:/home/ece792/Project2'))

#call automation
subprocess.call(shlex.split('sudo'+' '+'ansible-playbook'+' '+'automate.yml'+ ' '+'-i' +' ' +'./inventory'+' '+'--extra-var'+ ' '+'inp_file='+arg_file))

#get ips after and do load balancing
with open(file_name,'r') as vmf:
    schema = json.load(vmf)

schema['vm_list_lb']=[]
for i in range(0,int(subnet_count)):
    for sub in schema['subnets']:
        for h in sub:
            for vms in h['vm_list']:
                schema['vm_list_lb'].append(vms['ip'])

li = schema['vm_list_lb']
for n,vm_ip in enumerate(li):
    subprocess.call(shlex.split('./loadBalanceAdd.sh'+' '+str(n+1)+' '+'70.70.70.70'+' '+get_ip(ps_host1_subnet,2)+' '+'5678'+' ' +vm_ip+' '+'22'+' '+NS_name))
    #schema['vm_list_lb'].append({h['subnet_name'] : li})

with open(file_name,'w') as ofile1:
    json.dump(schema,ofile1,indent=4)

subprocess.call(shlex.split('sudo scp'+' ' +file_name+' '+' ece792@172.16.12.12:/home/ece792/Project2'))

#call cron job here for monitoring
#subprocess.call(shlex.split('sudo python'+' '+'startCron.py'+' '+file_name))





    




#subprocess.call(shlex.split('./setNS.sh '+NS_name+' '+ps_host1_subnet+' '+ps_host2_subnet))

#gre_name = NS_name+"_gre"
#local_ip = get_ip(ps_host1_subnet,2)
#remote_ip = get_ip(ps_host2_subnet,2)
#n_hop = '100.100.100.1'
#next_hop = '172.16.12.12'
#subprocess.call(shlex.split('./addTenantGRETunnel.sh '+NS_name+' ' +gre_name+' '+local_ip+' '+remote_ip+' '+n_hop+' '+ next_hop))


#for i in range(0,int(subnet_count)):
    #first_ip_range = get_ip(subnet_list[i],10)
    #last_ip_range = get_ip(subnet_list[i],240)
    #subnet_name = tenant_name + "S"+str(i+1)
    #subprocess.call(shlex.split('./addTenantSubnet.sh '+NS_name+' '+str(i+1)+' '+subnet_list[i]+' '+prefix_list[i]+' '+first_ip_range+' '+last_ip_range+' '+subnet_name))


#def get_mac(vm):
   # conn = libvirt.open('qemu:///system')
    #print vm
    #dom =conn.lookupByName(vm)
    #while(True):
        #if(dom.isActive() == 1):
          # break

    #mac=''
    #ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    #for (name, val) in ifaces.iteritems():
        #if name != "lo":
           # mac =val['hwaddr']
    #return mac

#def extract_ip(vm):
    #conn = libvirt.open('qemu:///system')
    #dom = conn.lookupByName(vm)
    #ip=' '
    #ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    #for (name,val) in ifaces.iteritems():
        #if name !="lo":
             #if val['addrs']:
                #for ipaddr in val ['addrs']:
                    #if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        #ip = ipaddr['addr']
    #return ip

#with open(file_name,'r') as t_f:
    #schema = json.load(t_f)


#for k in schema['subnets']:
    #for h in k:
        #if h['host'] == 'host1':
            #for vms in h['vm_list']:
                #vm = vms['name']
                #subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'create_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                #subprocess.call(shlex.split('./addVMBridgeInterface.sh'+' '+NS_name+' '+h['bridge']+' ' +vm))
                #subprocess.call(shlex.split('./addDomainInterface.sh'+' '+vm+' '+h['bridge']))
                #subprocess.call(shlex.split('sudo'+' ' +'ansible-playbook'+' ' +'start_vm.yml'+' '+'--extra-var' +' '+'vm_name='+vm))
                #print(vm)
                #time.sleep(40)
                #mac_address = get_mac(vm) 
                ##subprocess.call(shlex.split('./addStaticIP.sh'+' '+mac_address+' '+vm+' '+vms['ip']+' '+NS_name+' '+h['subnet_name']))
                #ip_get = extract_ip(vm)
                #vms['ip'] = ip_get

#with open(file_name,'w') as tt_f:
    #json.dump(file_name,tt_f,indent=4)





    
        
        

