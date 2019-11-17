from crontab import CronTab

cron = CronTab(user='ece792')
job = cron.new(command='python /home/ece792/Project/Test/getStats.py 0.0',comment='sample_cron')
job.minute.every(2)

cron.write()
