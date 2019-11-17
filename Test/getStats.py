import libvirt
import sys
from time import sleep
import os
from datetime import datetime


conn = libvirt.open('qemu:///system')

if conn == None:
    print("Failed to open")
    exit(1)

#cond = sys.argv[1]
#domain_id = conn.listDomainsID() #gives list of all domainids

cpu_usage = {}
mem_usage = {}


#threshold = float(sys.argv[1]) #expecting threshold to be given by tenant 

def get_CPU(vm_name):
    dom = conn.lookupByName(vm_name)
    cpu = dom.getCPUStats(True)
    for cpus in cpu:
        start_cycle = cpus['cpu_time']/1000000000.
    sleep(1)
    cpu =dom.getCPUStats(True)
    for cpus in cpu:
        end_cycle = cpus['cpu_time']/1000000000.
    cpu_usage = end_cycle-start_cycle
    return cpu_usage


    #for vm in domain_id:
     #   start_cycle =0
     #   end_cycle =0
     #   dom = conn.lookupByID(vm)
     #   cpu = dom.getCPUStats(True)
     #   for cpus in cpu: 
     #       start_cycle = cpus['cpu_time']/1000000000.
     #   sleep(1)
     #   cpu =dom.getCPUStats(True)
     #   for cpus in cpu:
     #       end_cycle = cpus['cpu_time']/1000000000.
     #   cpu_usage[dom.name()] = end_cycle-start_cycle

    #cpu_usage = sorted(cpu_usage.items(),key=lambda x: x[1])

    #writing to alerts.csv
    #if not os.path.isfile("/home/ece792/Project/Test/alerts.csv"):
    #    f = open("/home/ece792/Project/Test/alerts.csv",'w')
    #    f.write("VM Name, Timestamp, CPU usage\n")
    #else:
    #    f = open("/home/ece792/Project/Test/alerts.csv",'a')


    #for vm in cpu_usage:
    #    dom = conn.lookupByName(vm[0])
    #    if vm[1] > threshold:
    #        f.write(vm[0] +", "+str(datetime.now())+", "+str(vm[1])+"\n")

    #f.close()

#print(cpu_usage)

#checking memory
def get_MEM(vmname):

    dom = conn.lookupByName(vm_name)
    mem = dom.memoryStats()
    for name in mem:
        available = mem['available']
        total = mem['actual']
    mem_usage = 1-(available/total)
    return mem_usage






    #for vm in domain_id:
     #   dom = conn.lookupByID(vm)
      #  stats = dom.memoryStats()
       # for name in stats:
       #     available = stats['available']
        #    total = stats['actual']
       # mem_usage[dom.name()] = 1-(available/total)

   # mem_usage = sorted(mem_usage.items(),key=lambda x: x[1])
#print(mem_usage)
    #if not os.path.isfile("/home/ece792/Project/Test/mem_alerts.csv"):
     #   f = open("/home/ece792/Project/Test/mem_alerts.csv",'w')
     #   f.write("VM Name, Memory usage\n")
    #else:
     #   f = open("/home/ece792/Project/Test/mem_alerts.csv",'a')

    #for vm in mem_usage:
    #    dom = conn.lookupByName(vm[0])
    #    f.write(vm[0] +","+str(vm[1])+"\n")


def main():
    #after testCron is executed 
    #expect to have tenant's vm and threshold details
    #rough code below need to write code with alignement to north bound data model

    for tenant in tenants:
        for vm in tenant_vms:
            cpu_stat = getCPU(vm)
            mem_stat = getMEM(vm)

            job = getScalingDecision(cpu_stat,mem_stat)

            if job == 1:
                #do scale up

            elif job ==2:
                #do scale down

            else:
                #no need to do anything


