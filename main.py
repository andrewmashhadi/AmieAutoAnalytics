##### LOAD LIBRARIES
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import yaml
import os
from datetime import datetime, timedelta
import pytz

##### AMIE LIBRARIES
from auto_analytics.auto_analytics_collection import *
from auto_analytics.auto_analytics_utils import *


#### HELPER FUNCTIONS


#### MAIN DEFINITION
def main(auto_settings):
    pass


####

if __name__ == "__main__":

    #### LOAD SETTINGS
    with open('/home/ec2-user/lt_ml/auto-buffer-status/config.yaml', 'r') as file:
        auto_settings = yaml.safe_load(file)
    ####

    main(auto_settings)