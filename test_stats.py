import json
import subprocess
import shlex

li = "C1_1,C1_2"
li1 = "test1"
#output = subprocess.check_output('python container_stats_1.py '+li,shell=True)  # working for local host
#output = subprocess.check_output('ssh ece792@172.16.12.12 sudo python /home/ece792/eg1.py ',shell=True)
#output = subprocess.check_output('ssh ece792@172.16.12.12 sudo python /home/ece792/container_stats_1.py '+li1,shell=True)

#print(output.strip())
#output = output.strip().split(' ')
#print(output)
#cpu = output[0]
#mem = output[1]

#print(cpu)
#print(mem)

output = subprocess.check_output('./hypervisorStats.sh ',shell=True)
print(output.strip())
output1 = subprocess.check_output('ssh ece792@172.16.12.12 sudo /home/ece792/hypervisorStats.sh ' ,shell=True)
print(output1.strip())

subprocess.call(shlex.split('ssh ece792@172.16.12.13 sudo -W ignore /home/ece792/hypervisorStats.sh '))

