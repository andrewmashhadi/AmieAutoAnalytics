#!/bin/bash

source /home/ec2-user/.bashrc # for env variables
source /home/ec2-user/miniconda3/etc/profile.d/conda.sh  

# Activate the Conda environment
conda activate aaa-env

echo ""
echo "***********************************************************************************************************"
echo "********************** Current date and time in PST: $(TZ='America/Los_Angeles' date) **********************"
echo "***********************************************************************************************************"
echo " "

# Run the Python script
python /home/ec2-user/projects/AmieAutoAnalytics/main.py  # Replace with the correct path to your Python script

# Deactivate Conda environment
conda deactivate