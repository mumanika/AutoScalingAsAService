import os
import subprocess
import sys
import docker 


def cont_cpu_stats():
	
	list_ = sys.argv[1]
        cont_list = list_.split(",")
        #print(cont_list)
        total_cpu =0
        total_mem =0
        hyp_cont_cpu =[]
        hyp_cont_mem=[]
        cont_cpu_stats={}
        cont_mem_stats={}

        os.system("sudo docker stats --no-stream > /home/ece792/AutoScalingAsAService/dockerstats")
        with open("/home/ece792/AutoScalingAsAService/dockerstats",'r') as f:
        	for row in f:
                	list = row.strip('\n').split()
                	id_ =str(list[0])
                	cont_cpu_stats[id_[:10]] =list[2]
                        cont_mem_stats[id_[:10]] =list[6]
        
        cont_cpu_stats.pop('CONTAINER',None)
        cont_mem_stats.pop('CONTAINER',None)
        #print(cont_cpu_stats)
        #print(cont_mem_stats)

        client = docker.from_env()
        for item in cont_list:
	    if item is not "":
                cont_id = str(client.containers.get(item).short_id)
                #print(cont_id)
                if cont_id in cont_cpu_stats:
                        hyp_cont_cpu.append(cont_cpu_stats[cont_id])
                        hyp_cont_mem.append(cont_mem_stats[cont_id])
        #print(hyp_cont_cpu)

        for i in range(len(hyp_cont_cpu)):
                total_cpu = total_cpu + float(hyp_cont_cpu[i].strip("%"))
                total_mem = total_mem + float(hyp_cont_mem[i].strip("%"))

        cont_cpu_avg = total_cpu
        cont_mem_avg = total_mem

        print cont_cpu_avg, cont_mem_avg



def main():
        cont_cpu_stats()


if __name__ == '__main__':
        main()
