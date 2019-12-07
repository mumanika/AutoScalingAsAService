import json

# This API can be called by the client from a python file to create their VPC
# Args: number of subnets you want to spawn (int), the subnets' details in a predefined format, the scaling groups list in a predefined format

def VPCSetupAPI(subnet_num,subnetsList,scalingGroupsList):
    jsonDump = {};
    jsonDump["subnet_count"] = subnet_num;
    jsonDump["subnets"] = subnetsList;
    jsonDump["scaling_groups"] = scalingGroupsList;
    with open('input_T1.json','w') as w_f:
        json.dump(jsonDump,w_f,indent=4);
