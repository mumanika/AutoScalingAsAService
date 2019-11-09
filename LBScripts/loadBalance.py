import os

def addEntryToLB(index,namespaceIP,namespacePort,vmIP,vmPort):
    os.system("./loadBalanceAdd.sh "+index+" "+namespaceIP+" "+namespacePort+" "+ vmIP+" "+vmPort);

def deleteEntryInLB(index,namespaceIP,namespacePort,vmIP,vmPort):
    #jsonFile is the fd of the file already opened by the caller
    os.system("./loadBalanceRep.sh "+index+" "+namespaceIP+" "+namespacePort+" "+ vmIP+" "+vmPort);
