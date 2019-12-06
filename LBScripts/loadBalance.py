import subprocess as s

def addEntryToLB(index,namespaceIP,namespacePort,vmIP,vmPort, nsName):
    s.call("./loadBalanceAdd.sh "+index+" "+namespaceIP+" "+namespacePort+" "+ vmIP+" "+vmPort+" "+nsName);

def deleteEntryInLB(index,namespaceIP,namespacePort,vmIP,vmPort,nsName):
    #jsonFile is the fd of the file already opened by the caller
    s.call("./loadBalanceRep.sh "+index+" "+namespaceIP+" "+namespacePort+" "+ vmIP+" "+vmPort+" "+nsName);
