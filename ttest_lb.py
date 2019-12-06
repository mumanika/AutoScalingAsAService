import json
import subprocess
import shlex


get_ip = subprocess.check_output("sudo docker container exec --privileged LC1 ip -4 addr show eth0 | grep -oP \'(?<=inet\s)\d+(\.\d+){3}\'", shell=True).strip()
print(get_ip)
