from datetime import datetime
myFile = open('/home/ece792/Project/Test/append.txt','a')
myFile.write('\n Acc on '+str(datetime.now()))
myFile.close()
