import sys
from crontab import CronTab

file_name = sys.argv[1]

cron = CronTab(user='ece792')
job = cron.new(command='python /home/ece792/AutoScalingAsAService/monitor.py'+' ' +file_name,comment='sample_cron')
job.minute.every(2)

cron.write()
