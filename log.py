"""This file is for the logging"""

import logging
import os
os.getcwd()

file_name="log.txt"
if not os.path.exists(file_name):
      open(file_name,'w').close() # create an empty log file
      log_message='Log file created successfully !'
      
else:
      log_message='Failed to create the log_file !'

# setup log config and creating a file handler
logging.basicConfig(filename=file_name,
                    level=logging.WARNING,
                    format="%(asctime)s-%(levelname)s-%(message)s",force=True)
handler=logging.FileHandler(file_name)
handler.setLevel(logging.WARNING)
formatter=logging.Formatter('%(name)s-%(asctime)s-%(levelname)s-%(message)s')

handler.setFormatter(formatter)

logging.getLogger('').addHandler(handler)

# log file creation status
logging.info(log_message)

# logging functions
def log_info(msg):
      logging.info(msg)
      
def log_warning(msg):
      logging.warning(msg)
      
def log_critical(msg):
      logging.critical(msg)
      
def log_error(msg):
      logging.error(msg)
      
if __name__=="__main__":
      log_info('Looging System initialized !')
      log_warning('This is the warning message !')
      log_critical('This is the critical error !')
      log_error('This is the ERROR message !')

