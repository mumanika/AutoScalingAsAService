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
    return int(dtime.total_seconds())

def update_json(schema):
    with open(file_name,'w') as w_f:
        json.dump(schema,w_f,indent=4)

    for host in mgmt_schema['hosts']:
        if host['mgmt_ip'] == '172.16.12.13':
            continue
        else:
            subprocess.call(shlex.split('sudo scp '+file_name+' ' +host['user']+'@'+host['mgmt_ip']+':/home/ece792/AutoScalingAsAService/'))

def get_ip(address,last_idx):
    sub = address.split('.')
    ip =''
    for n,p in enumerate(sub):
        if n != len(sub)-1:
            ip = ip + p+'.'
    ip = ip+str(last_idx)
    return ip




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
            timer = datetime.strptime(grp_meta['timer'], '%Y-%m-%d %H:%M:%S.%f');
            break


    if flag ==1 and scale_up_ct >0:    # first time scaling up no need to check cooldown. Check only for flag
        for grp_meta in schema['scaling_metadata']:
            if grp_meta['name'] == grp_name:
                 grp_meta['flag']= 0
                 grp_meta['timer'] = str(datetime.now())
        #update json
        update_json(schema)
        return 1

    elif flag ==0 and scale_up_ct >0:    #check for cooldown period else wise
        p_timer = datetime.now();
        if int(diff(p_timer - timer)) > int(60*schema['cooldown']):
            for grp_meta in schema['scaling_metadata']:
               if grp_meta['name'] == grp_name:
                    grp_meta['timer'] = str(p_timer)
            #update json tbd
            update_json(schema)
            return 1

        else:
            return 0

    #if no scale up then need to check scale down
    
    for m in range(min(scale_down_ct,len(cont_dict)-min_cont),0,-1):
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
        grp_subnets  = grp[0]['members']
        
        print(action)
        if action == 1:  #scale up
            min_hyp_use = 100
            hyp_ip=''
            hyp_user=''
            for hyp_host in mgmt_schema['hosts']:
                if hyp_host['mgmt_ip'] == '172.16.12.13':
                    output = subprocess.check_output('/home/ece792/AutoScalingAsAService/hypervisorStats.sh ' ,shell=True).strip()
                else:

                    output = subprocess.check_output('ssh '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+'  /home/ece792/AutoScalingAsAService/hypervisorStats.sh ' ,shell=True).strip()
                #print(output)
                if float(output) <  min_hyp_use:
                    min_hyp_use = float(output)
                    hyp_ip = hyp_host['mgmt_ip']
                    hyp_user = hyp_host['user']

            print(hyp_ip)

            for host in mgmt_schema['hosts']: #get host_name
                if host['mgmt_ip'] == hyp_ip:
                    host_name = host['host']

            subnet_name = ''
            rand_id = random.choice(grp_subnets)

            for sub in schema['subnets']:
                flag =1
                for h in sub:
                     if h['subnet_id'] ==  rand_id:
                        subnet_name = h['subnet_name']
                        flag =0
                        break
                 if flag == 0:
                     break

            print(subnet_name)

            lb_base = False
            base_ns_subnet =''

            for sub in schema['subnets']:
                for h in sub:
                    if h['host'] == host_name and h['subnet_name'] == subnet_name:
                        if len(h['container_lb_list']) ==0:
                            lb_base = True
                        base_ns_subnet = h['base_ns_subnet']
            
            base_ns_subnet = get_ip(base_ns_subnet,2)
            if lb_base == True:
                n_packet = 0
                for sub in schema['subnets']:
                    for h in sub:
                        if h['subnet_id'] in grp_subnets:
                            if len(h['container_lb_list']) > 0:
                                n_packet +=1
            
                for hyp_host in mgmt_schema['hosts']:
                    if hyp_host['mgmt_ip'] == '172.16.12.13':
                        subprocess.call(shlex.split(' sudo  /home/ece792/AutoScalingAsAService/loadBalanceBaseAdd.sh '+str(n_packet+1)+' '+base_ns_subnet+' 1025  '+schema['ns_name']+ ' ' +grp[0]['name']))

                    else:
                        subprocess.call(shlex.split('ssh  '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+' sudo  /home/ece792/AutoScalingAsAService/loadBalanceBaseAdd.sh '+str(n_packet+1)+' '+base_ns_subnet+' 1025  '+schema['ns_name']+ ' ' +grp_name))



            if hyp_ip == '172.16.12.13':
                subprocess.call(shlex.split(' python  /home/ece792/AutoScalingAsAService/scale_up.py '+file_name+' '+hyp_ip+' ' +grp[0]['name']+' '+subnet_name))
            else:
                subprocess.call(shlex.split('ssh '+hyp_user+'@'+hyp_ip+' python  /home/ece792/AutoScalingAsAService/scale_up.py '+file_name+' '+hyp_ip+' ' +grp[0]['name']+' ' +subnet_name))
        
        elif action == 0:
            continue

        else:
            action = action -2 # need to see scale down



if __name__=='__main__':
    main()

            



            

