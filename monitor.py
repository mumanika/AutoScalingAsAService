import json
import sys
import subprocess
import shlex
import time
from datetime import datetime

file_name = sys.argv[1]
with open(file_name,'r') as f:
    schema = json.load(f)

with open('mgmt.json','r') as mgmt_f:
    mgmt_schema = json.load(mgmt_f)

def diff(dtime):
    timer = dtime.split(":")[2]
    return float(timer)



def dynamic_reactive(grp,schema):
    mem = set(grp[0]['members'])
    min_cpu = grp[0]['policy']['min_cpu']
    min_cont = grp[0]['policy']['min_cont']
    max_cpu = grp[0]['policy']['max_cpu']
    max_mem = grp[0]['policy']['max_mem']
    grp_name = grp[0]['name']

    cont_dict ={}

    for sub in schema['subnets']:
        for h in sub:
            if h['subnet_id'] in mem:
                cont_list =''
            
                for machine in h['container_list']:
                    cont_list = machine['name']

                    if h['host'] == 'host1':
                        output = subprocess.check_output('sudo python container_stats_1.py '+cont_list,shell=True)
                    else:
                        output = subprocess.check_output('ssh ece792@172.16.12.12 sudo python /home/ece792/AutoScalingAsAService/container_stats_1.py '+cont_list,shell=True)

                    output = output.strip().split(' ')
                    #print(output)
                    cpu_stat = output[0]
                    mem_stat = output[1]
                    cont_dict[cont_list] = (cpu_stat,mem_stat)
            
    scale_up_ct =0
    scale_down_ct =0
    optimal_ct =0
    total_cpu = 0

    for key,value in cont_dict.items():
        print(value)
        cpu = float(value[0])
        mem = float(value[1])
        total_cpu += cpu
        if cpu > max_cpu or mem > max_mem:
            scale_up_ct +=1
        elif cpu < min_cpu:
            scale_down_ct +=1
        else:
            optimal_ct +=1

    if optimal_ct == len(cont_dict):  #no need of scale up or scale down
        return 0


    for grp_meta in schema['scaling_metadata']:
        if grp_meta['name'] == grp_name:
            flag = grp_meta['flag']
            timer = grp_meta['timer']
            break


    if flag ==1 and scale_up_ct >0:    # first time scaling up no need to check cooldown. Check only for flag
        for grp_meta in schema['scaling_metadata']:
            if grp_meta['name'] == grp_name:
                 grp_meta['flag']= 0
                 grp_meta['timer'] = datetime.now()
        #update json


        return 1

    elif flag ==0 and scale_up_ct >0:    #check for cooldown period else wise
        p_timer = datetime.now()
        if diff(str(p_timer - timer)) > schema['cooldown']:
            for grp_meta in schema['scaling_metadata']:
               if grp_meta['name'] == grp_name:
                    grp_meta['timer'] = p_timer
            #update json tbd
            return 1

        else:
            return 0

    #if no scale up then need to check scale down
    
    for m in range(scale_down_ct,min_cont-1,-1):
        if total_cpu < (len(cont_dict) - m )* max_cpu:

            return m+2


    return 0





        


def get_action(grp,schema):
    action=0
    policy_type = grp[0]['policy']['type']
    if policy_type == 'dynamic':
        action = dynamic_reactive(grp,schema)

    return action

def main():
    #after testCron is executed
    #expect to have tenant's vm and threshold details
    #rough code below need to write code with alignement to north bound data model

    

    for grp in schema['scaling_groups']:
        #self_heal(grp,schema)
        action = get_action(grp,schema)
        
        print(action)
        if action == 1:  #scale up
            min_hyp_use = 100
            hyp_ip=''
            hyp_user=''
            for hyp_host in mgmt_schema['hosts']:

                output = subprocess.check_output('ssh '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+' /home/ece792/AutoScalingAsAService/hypervisorStats.sh ' ,shell=True).strip()
                if float(output) <  min_hyp_use:
                    min_hyp_use = float(output)
                    hyp_ip = hyp_host['mgmt_ip']
                    hyp_user = hyp_host['user']

            print(hyp_ip)
            subprocess.call(shlex.split('ssh '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+' python  /home/ece792/AutoScalingAsAService/scale_up.py '+file_name+' '+hyp_ip+' ' +grp[0]['name']))
        
        elif action == 0:
            continue

        else:
            action = action -2 # need to see scale down



if __name__=='__main__':
    main()

            



            

