import logging
logger = logging.getLogger('gumstix.sensors.sensor')

import random

import threading
import types
from time import sleep

class sensor(threading.Thread):
    def __init__(self, port, name, interval):
        threading.Thread.__init__(self)
        self.port = port #What pin sensor is on
        self.name = name #naming thread, why?
        self.interval = interval #data collection time interval
        self.stopEvent = threading.Event() #stop the data collection
        self.killEvent = threading.Event() #data collected, kill thread
        logger.debug('Sensor Setup' #Debug as also logged in controls
                    + '\n \t Number \t' + str(self.no) 
                    + '\n \t Name \t' + str(self.name)
                    + '\n \t Interval \t' + str(self.interval))
    
    def run(self):
        self.sensor_data = []
        while not self.stopEvent.isSet():
            sleep(self.interval)
            self.sensor_data.append(random.randint(1, 10))
        while not self.killEvent.isSet(): # Wait till data collected
            sleep(100)
    
    def collect(self):
        sensor_data = self.sensor_data
        self.sensor_data = []

        if self.stopEvent.isSet():
            self.killEvent.set()
            logger.info('Sensor ' + str(self.no) + 'kill event set')
        return sensor_data
    
    def update(self, interval):
        logger.debug('Sensor ' + str(self.no) + ' Interval ' + str(interval))
        if interval == 0:
            self.stopEvent.set()
            logger.info('Sensor ' + str(self.no) + 'stop event set')
            self.interval = 0
        elif (interval != 0) and (interval.isnumeric()):
            self.interval = interval
            logger.debug('Sensor ' + str(self.no) + ' Interval Updated ' + str(self.interval))
        else: #error with sent message
            logger.error('Sensor ' + str(self.no) + ' Update Failed ' + str(interval))
        