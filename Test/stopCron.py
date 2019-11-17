from crontab import CronTab

cron = CronTab(user="ece792")

job = cron.find_comment('sample_cron')
cron.remove(job)
cron.write()
