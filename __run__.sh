#!/bin/bash

source /home/ec2-user/.bashrc # for env variables
source /home/ec2-user/miniconda3/etc/profile.d/conda.sh  
conda activate aaa-env

echo ""
echo "***********************************************************************************************************"
echo "********************** Current date and time in PST: $(TZ='America/Los_Angeles' date) **********************"
echo "***********************************************************************************************************"
echo " "
python /home/ec2-user/AmieAutoAnalytics/main.py

# Deactivate Conda environment
conda deactivate