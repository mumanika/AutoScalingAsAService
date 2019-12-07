import subprocess
import shlex
import sys

ip = str(sys.argv[1]);
port = "1025";
c_name = str(sys.argv[2]);
subnet_name = str(sys.argv[3]);
ruleNo = str(sys.argv[4]); 

subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/deleteContainer.sh '+c_name));
subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/deleteGuestBridgeInterface.sh '+subnet_name+' '+c_name));
subprocess.call(shlex.split('sudo /home/ece792/AutoScalingAsAService/loadBalanceRep.sh '+ruleNo+' '+ip+' '+port+' '+subnet_name+' '+ruleNo));
