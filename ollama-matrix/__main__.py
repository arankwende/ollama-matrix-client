import yaml
import time
import os
import sys
import logging
import logging.handlers as handlers
import base64
import argparse
#import daemon
import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText
from ollama_matrix import OllamaMatrixClient



try:
    parser = argparse.ArgumentParser(description='This is a simple python script to connect Ollama to a Matrix Homeserver.')
    parser.add_argument('-c', action='store_true', help='Run with a custom config.')
    parser.add_argument('-d', action='store_true', help='Run as a daemon.')
    parser.add_argument('-DEBUG', action='store_true', help='Add Debug messages to log.')
    args = parser.parse_args()
except Exception as exception:
    logging.critical(f"There was a problem with the arguments you set. The exception is {exception}")

#We define the logic and place where we're gonna log things
log_dir = os.path.dirname(os.path.realpath(__file__))  
log_fname = os.path.join(log_dir, 'config','ollama_matrix.log') #I define a relative path for the log to be saved on the same folder as my config file
formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
logger = logging.getLogger() # I define format and instantiate first logger
fh = handlers.RotatingFileHandler(log_fname, mode='w', maxBytes=100000, backupCount=3) #This handler is important as I need a handler to pass to my daemon when run in daemon mode
fh.setFormatter(formatter) 
logger.addHandler(fh)
#And we define the attributes when running the program
if getattr(args,'DEBUG'):
    logger.setLevel(logging.DEBUG) 
    fh.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
if getattr(args,'c'):
    logging.info("Running with -c, loading custom config")  
if getattr(args,'d'):
    logging.info("Running with -d in daemon mode.")
if getattr(args,'DEBUG'):
    logging.info("Running with -DEBUG in DEBUG log mode.")
#if getattr(args,'d'):
#    config, configuration = load_config()
#    context = daemon.DaemonContext(files_preserve = [configuration, fh.stream] )
#    with context:
#        main(args)

if __name__== '__main__':
        file_location = os.path.dirname(os.path.realpath(__file__))
        OMClient=OllamaMatrixClient(args)
        asyncio.run(OMClient.main())