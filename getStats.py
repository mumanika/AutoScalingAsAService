import libvirt
import sys
from time import sleep
import os
from datetime import datetime
import subprocess
import json
import shlex

file_name = sys.argv[1]
with open(file_name,'r') as f:
    schema = json.load(f)

conn = libvirt.open('qemu:///system')

if conn == None:
    print("Failed to open")
    exit(1)


cpu_usage = {}
mem_usage = {}



def getCPU(vm_name):
    dom = conn.lookupByName(vm_name)
    cpu = dom.getCPUStats(True)
    for cpus in cpu:
        start_cycle = cpus['cpu_time']/1000000000.
    sleep(1)
    cpu =dom.getCPUStats(True)
    for cpus in cpu:
        end_cycle = cpus['cpu_time']/1000000000.
    cpu_usage = end_cycle-start_cycle
    return cpu_usage*100



#checking memory
def getMEM(vmname):

    dom = conn.lookupByName(vm_name)
    mem = dom.memoryStats()
    for name in mem:
        available = mem['available']
        total = mem['actual']
    mem_usage = 1-(available/total)
    return mem_usage*100


def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip


def getScalingDecision(cpu_stat,mem_stat,cpu_threshold,mem_threshold):
    if(cpu_stat > int(cpu_threshold) or mem_stat > int(mem_threshold)):
        print("entered")
        return 1;
    return 0;




def main():
    #after testCron is executed 
    #expect to have tenant's vm and threshold details
    #rough code below need to write code with alignement to north bound data model
    
    ns_ps_subnet = ' '
    for ns_ps in schema['ns_ps subnet']:
        if ns_ps['host'] == 'host1':
            ns_ps_subnet = ns_ps['ns_ps_subnet']

    ns_ps_subnet = get_ip(ns_ps_subnet,2)
    
    flag =0
    for sub in schema['subnets']:
        for h in sub:
            if h['host'] == 'host1':
                for vms in h['vm_list']:
                    cpu_stat = getCPU(vms['name'])
                    mem_stat = getCPU(vms['name'])
                    print(cpu_stat)
                    print(mem_stat)
                    print("cpu_threshold is "+h['cpu_threshold'])
                    job = getScalingDecision(cpu_stat,mem_stat,h['cpu_threshold'],h['mem_threshold'])

                    if job == 1: # do scale up
                        #hyp = getHypervisor()
                        n = h['vm_num']
                        vm_new_name = schema['ns_name']+"V"+str(int(n)+1)
                        os.system('sudo'+' ' +'ansible-playbook'+' '+'scale_up.yml'+' -i ./inventory '+'-e'+' '+'inp_file='+file_name+' '+'-e'+' '+'vm_name='+vm_new_name+' '+'-e'+' '+'ns_name='+schema['ns_name']+' '+'-e'+' '+'bridge_name='+h['bridge'])
                        #f.close()
                        #break
                

                        with open(file_name,'r') as gg:
                            sc = json.load(gg)
    
                        dest_ip = sc['vm_list_lb']
                        ip = dest_ip[len(dest_ip)-1]
                        subprocess.call(shlex.split('./loadBalanceAdd.sh'+' '+str(len(dest_ip))+' '+'70.70.70.70'+' ' +ns_ps_subnet+' '+'5678'+' '+ip+' '+'22'+' '+sc['ns_name']))
                        flag =1
                        break
            if flag ==1:
                break
        if flag ==1:
            break
                
            
if __name__=='__main__':
    main()      


            #if job == 1:
                #do scale up
             #   subprocess.call(shlex.split('sudo'+' '+'ansible-playbook'+' '+'automate.yml'+ ' '+'-i' +' ' +'./inventory'+' '+'--extra-var'+ ' '+'inp_file='+arg_file));
            #elif job ==2:
                #do scale down

            #else:
                #no need to do anything


