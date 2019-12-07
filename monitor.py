import json
import sys
import subprocess
import shlex
import time
import random
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
    
    print(scale_down_ct)
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
    if flag ==0 and scale_down_ct >0:
        #print("Entered")
        p_timer = datetime.now();
        if int(diff(p_timer - timer)) > int(60*schema['cooldown']):
            for grp_meta in schema['scaling_metadata']:
               if grp_meta['name'] == grp_name:
                    grp_meta['timer'] = str(p_timer)
            #update json tbd
            update_json(schema)

            for m in range(min(scale_down_ct,len(cont_dict)-min_cont),0,-1):
                if total_cpu < (len(cont_dict) - m )* max_cpu:
                    return m+2
        else:
            return 0


    return 0





def delete(ip,h_name,sub_name,grp_name,base_ns):
    with open(file_name,'r') as ff:
        n_schema = json.load(ff)

    lb = False




    
    for sub in n_schema['subnets']:
        for h in sub:
            if h['host'] == h_name and h['subnet_name'] == sub_name:
                h['container_lb_list'].remove(ip)

                for i in range(0,len(h['container_list'])):
                    #print(i)
                    #print(h['container_list'][i])
                    if h['container_list'][i]['ip'] == ip:
                        del h['container_list'][i]
                        break

                if len(h['container_lb_list']) == 0:
                    n_pack = subprocess.check_output('ip netns exec '+n_schema['ns_name']+ ' iptables -t nat -L '+grp_name+' --line-numbers | awk -v var=\"to:'+base_ns+':1025\" \'{for (I=1;I<=NF;I++) if ($I == var) {printf \"\%s\", $(1) };}\'',shell=True).strip()
                    n_rules = subprocess.check_output('ip netns exec '+n_schema['ns_name']+ ' iptables -t nat -L '+grp_name+' --line-numbers | awk \'END{printf \"\%s\", $(1) }\'',shell=True).strip()
                    #print(n_rules)
                    #print(n_pack)
                    #print(base_ns)
                    #print(grp_name)
                    subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/loadBalanceBaseRep.sh '+str(int(n_rules)-int(n_pack)+1)+' '+n_schema['ns_name']+' '+str(n_rules)+' ' +grp_name))
                    subprocess.call(shlex.split('ssh ece792@172.16.12.12 sudo  /home/ece792/AutoScalingAsAService/loadBalanceBaseRep.sh '+str(int(n_rules)-int(n_pack)+1)+' '+n_schema['ns_name']+' '+str(n_rules)+' ' +grp_name))

                update_json(n_schema)

                return

def update_log_file(file_name,hyp_ip,subnet_name):
    with open(file_name,'r') as log_f:
        log_schema = json.load(log_f)
    h_name =''
    if hyp_ip == '172.16.12.12':
        h_name = 'host2'
    else:
        h_name = 'host1'

    l_f = open(log_schema['log_file'],'a+')
    for sub in log_schema['subnets']:
        for h in sub:
            if h['host'] == h_name and h['subnet_name'] == subnet_name:
                l_f.write(str(datetime.now())+' : SCALE UP :New Container  with IP:'+h['container_lb_list'][len(h['container_lb_list'])-1] +' on '+ hyp_ip+ ' host\n')

                    


def get_action(grp,schema):
    action=0
    policy_type = grp[0]['policy']['type']
    if policy_type == 'dynamic':
        action = dynamic_reactive(grp,schema)

    return action

def del_no_lb(ip,h_name,sub_name,grp_name,base_ns):
    print("Entered del_no_lb")
    with open(file_name,'r') as ff:
        n_schema = json.load(ff)


    for sub in n_schema['subnets']:
        for h in sub:
            if h['host'] == h_name and h['subnet_name'] == sub_name:
                n_pack = h['container_lb_list'].index(ip)
                if h_name == 'host1':
                    subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/loadBalanceRep.sh '+str(n_pack+1)+' '+base_ns+' 1025'+' '+sub_name+' '+str(len(h['container_lb_list']))))
                else:
                     subprocess.call(shlex.split('ssh ece792@172.16.12.12 sudo /home/ece792/AutoScalingAsAService/loadBalanceRep.sh '+str(n_pack+1)+' '+base_ns+' 1025'+' '+sub_name+' '+str(len(h['container_lb_list']))))

                h['container_lb_list'].remove(ip)

                for i in range(0,len(h['container_list'])):
                    #print(i)
                    #print(h['container_list'][i])
                    if h['container_list'][i]['ip'] == ip:
                        del h['container_list'][i]
                        break


                update_json(n_schema)

                return



def self_heal(grp,schema):   #def delete(ip,h_name,sub_name,grp_name,base_ns):
    
    with open(file_name,'r') as nnf:
        nn_schema = json.load(nnf)

    mem = set(grp[0]['members'])
    
    miss_list =[]
    map_dict = {}

    for sub in schema['subnets']:
        for h in sub:
            if h['subnet_id'] in mem:
                cont_list =[]

                for machine in h['container_list']:
                    cont_list.append(str(machine['name']))
                    map_dict[machine['name']] = machine['ip']
                if(len(cont_list)):
                    cont_str = str(cont_list[0])
                    for j in range(1,len(cont_list)):
                        cont_str = cont_str+ cont_list[j];
                        if(j<(len(cont_list)-1)):
                            cont_str = cont_str + ',';

                    print("Cont_list ",cont_str);
                
                    if h['host'] == 'host1' and cont_str != str(''):
                        output = subprocess.check_output('sudo python container_stats.py '+cont_str,shell=True).strip()
                        output = output.split(",")
                        for item in output:
                            if item is not str(""):
                                miss_list.append((map_dict[item],h['host'],h['subnet_name'],grp[0]['name'],get_ip(h['base_ns_subnet'],2)))

                    elif cont_str != str(''):
                        output = subprocess.check_output('ssh ece792@172.16.12.12 sudo python /home/ece792/AutoScalingAsAService/container_stats.py '+cont_str,shell=True).strip()
                        output = output.split(",")
                        for item in output:
                            if item is not "":
                                miss_list.append((map_dict[item],h['host'],h['subnet_name'],grp[0]['name'],get_ip(h['base_ns_subnet'],2)))
   
    print(" missing list is ",miss_list)
    #delete lb rules for missing containers
    for tup in miss_list:
        del_no_lb(tup[0],tup[1],tup[2],tup[3],tup[4])

    #spawn new container in respective subnets
    with open(file_name,'r') as nnf:
        nn_schema = json.load(nnf)

    for tup in miss_list:
        cont_id = nn_schema['total_ct']
        cont_id +=1
        nn_schema['total_ct'] = cont_id
        sub_id = tup[2][1]
        cont_name = 'C'+str(sub_id)+'_'+str(cont_id)

        if tup[1] == 'host1':
            subprocess.call(shlex.split('./createContainer.sh'+' '+cont_name+' '+tup[2]))
        else:
            subprocess.call(shlex.split('ssh ece792@172.16.12.12 sudo /home/ece792/AutoScalingAsAService/createContainer.sh '+cont_name+' '+tup[2]))
        ip_get = subprocess.check_output("sudo docker container exec --privileged "+cont_name+" ip -4 addr show "+cont_name+tup[2]+"B | grep -oP \'(?<=inet\s)\d+(\.\d+){3}\'", shell=True).strip()

        idx =0

        for sub in nn_schema['subnets']:
            for h in sub:
                if h['host'] == tup[1] and h['subnet_name'] == tup[2]:

                    h['container_list'].append({
                        "ip":ip_get,
                        "name":cont_name
                     })
                    h['container_lb_list'].append(ip_get)
                    idx = len(h['container_lb_list'])
                    break



        subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/loadBalanceAdd.sh '+str(idx)+' '+tup[4]+' 1025 '+ip_get+' 22 '+ tup[2]))
        update_json(nn_schema)




        







def main():
    #after testCron is executed
    #expect to have tenant's vm and threshold details
    #rough code below need to write code with alignement to north bound data model

    

    for grp in schema['scaling_groups']:
        self_heal(grp,schema)
        with open(file_name,'r') as after_f:
            after_schema = json.load(after_f)
        action = get_action(grp,after_schema)
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

            for sub in after_schema['subnets']:
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

            for sub in after_schema['subnets']:
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
                        subprocess.call(shlex.split('ssh  '+hyp_host['user']+'@'+hyp_host['mgmt_ip']+' sudo  /home/ece792/AutoScalingAsAService/loadBalanceBaseAdd.sh '+str(n_packet+1)+' '+base_ns_subnet+' 1025  '+schema['ns_name']+ ' ' +grp[0]['name']))



            if hyp_ip == '172.16.12.13':
                subprocess.call(shlex.split(' python  /home/ece792/AutoScalingAsAService/scale_up.py '+file_name+' '+hyp_ip+' ' +grp[0]['name']+' '+subnet_name))
            else:
                subprocess.call(shlex.split('ssh '+hyp_user+'@'+hyp_ip+' python  /home/ece792/AutoScalingAsAService/scale_up.py '+file_name+' '+hyp_ip+' ' +grp[0]['name']+' ' +subnet_name))

            update_log_file(file_name,hyp_ip,subnet_name)
        
        ####### finished scale up #########
        
        elif action == 0:
            continue

        else:
            scale_down_ct = action -2 # need to see scale down
            log_f = open(schema['log_file'],'a+')

            scale_down_li = []
            total_li = []

            for sub in after_schema['subnets']:
                for h in sub:
                    if h['subnet_id'] in grp_subnets:
                        for num,x in enumerate(h['container_list']):
                            total_li.append((x['ip'],x['name'],h['host'],h['subnet_name'],h['base_ns_subnet'],num+1))

            scale_down_li = total_li[(-1*scale_down_ct):]

            for tup in scale_down_li:
                ip = tup[0]
                cont_name = tup[1]
                host_tbd = tup[2]
                subnet_name = tup[3]
                base_ns_subnet = tup[4]
                n_pack = tup[5]
                base_ns_subnet = get_ip(base_ns_subnet,2)
                
             


                if host_tbd == 'host1':
                    subprocess.call(shlex.split(' python /home/ece792/AutoScalingAsAService/scale_down.py '+base_ns_subnet+' '+cont_name+' '+subnet_name+' '+str(n_pack)))
                else:
                    subprocess.call(shlex.split('ssh ece792@172.16.12.12 python  /home/ece792/AutoScalingAsAService/scale_down.py '+base_ns_subnet+' '+cont_name+' '+subnet_name+' '+str(n_pack)))
                
                hyp_ip_1 =''
                if host_tbd == 'host1':
                    hyp_ip_1 = '172.16.12.12'
                else:
                    hyp_ip_1 = '172.16.12.13'

                log_f.write(str(datetime.now())+' : SCALE DOWN :Container  with IP:'+ip +' on '+ hyp_ip_1+ 'host\n')
                delete(ip,host_tbd,subnet_name,grp[0]['name'],base_ns_subnet)



                        






if __name__=='__main__':
    main()

            



            

