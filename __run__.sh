#!/bin/zsh

# Load Conda for Zsh (adjust the path to match your Conda installation)
source $HOME/.zshrc
source $HOME/opt/anaconda3/etc/profile.d/conda.sh 

# Activate the Conda environment
conda activate aaa-env

echo ""
echo "***********************************************************************************************************"
echo "********************** Current date and time in PST: $(TZ='America/Los_Angeles' date) **********************"
echo "***********************************************************************************************************"
echo " "

# Run the Python script
python $HOME/LiveProjects/AmieAutoAnalytics/main.py  # Replace with the correct path to your Python script

# Deactivate Conda environment
conda deactivate