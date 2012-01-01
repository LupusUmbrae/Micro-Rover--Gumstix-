import logging
logger = logging.getLogger('gumstix.sensors.controls')

# Re-Write sensor module
# Class sensor
#    def __init__
#    send all sensor configs
#
#    def update
#    Starts, stops, creates sensor threads
#
#    def status
#    Returns status of all currently running sensors
#
#    def getData
#    Returns sensor data for each sensor
#
# all sensors handled within this module not single instances
#

import threading
import sensor
import sensor_types
class sensor_controls():
    def __init__(self, sensor_no, sensor_name, sensor_interval, sensor_type):
        self.name = sensor_name #Reference the data
        self.no = sensor_no #use to identify which pin its attached too
        self.interval = sensor_interval #data collection interval
        self.type = sensor_type #to set type class in sensor thread
        logger.info('Sensor Settings'
                    + '\n \t Number \t' + str(self.no) 
                    + '\n \t Name \t \t' + str(self.name)
                    + '\n \t Interval \t' + str(self.interval)
                    + '\n \t Type \t \t' + str(self.type))
    
    def start(self):
        if self.interval != 0:
            logger.debug('Sensor Thread init - ' +self.name)
            self.obj = sensor.sensor(self.no, self.name, self.interval)
            #self.obj.setName(self.name)
            logger.debug('Starting Sensor Thread - ' + self.name)
            self.obj.start()
            self.type_setup()
    
    def type_setup(self):
        try:
            self.type_obj = getattr(sensor_types, self.type)
        finally:
            pass
            
    def collect(self):
        if self.interval != 0:
            sensor_data = self.obj.collect()
            sensor_data = self.type_obj.process(sensor_data)
            sensor_data = [self.name, sensor_data]
            return sensor_data
        else:
            return [self.name, [False]]
    
    def update(self, interval):
        self.obj.update(interval)