# AutoScalingAsAService
Keep all the files at same location
Run n_bound.py using below command
            " sudo python n_bound.py"
n_bound.py follows below flow :
    1. Create VPC Setup
    2. Calls Cron job
    3. Start monitoring the VPC setup
    4. At periodic interval, it will check the threshold value of CPU and Mem of Containers/VMS , and then take respective action of scale up/down
