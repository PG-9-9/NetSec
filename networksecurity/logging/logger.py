import logging
import os
from datetime import datetime

LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log" # month_day_year_hour_minute_second.log


logs_path=os.path.join(os.getcwd(), "logs",LOG_FILE) # /path/to/networksecurity/logs/month_day_year_hour_minute_second.log

os.makedirs(logs_path,exist_ok=True)

LOG_FILE_PATH=os.path.join(logs_path, LOG_FILE) # /path/to/networksecurity/logs/month_day_year_hour_minute_second.log/month_day_year_hour_minute_second.log

logging.basicConfig(filename=LOG_FILE_PATH, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')