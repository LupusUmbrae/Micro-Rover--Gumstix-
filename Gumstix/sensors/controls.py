import logging
import threading
import sensor
import sensor_types
logger = logging.getLogger('gumstix.sensors.controls')

# Re-Write sensor module
class sensorControl:
    def __init__(self, sensorsConfig):
        sensor = sensor.sensor
        self.sensorMap = {}
        for port, sensorConfig in sensorsConfig.iteritems():
            self.sensorMap[port] = sensor(port, sensorConfig[1], sensorConfig[2])
            

            
#    send all sensor configs
#
    def update(self, port, sensorConfig):
        if self.sensorMap.has_key(port):
            pass
        pass
#    Starts, stops, creates sensor threads
#

#    Return true for exists, false for not setup
    def status(self, port):
        if self.sensorMap.has_key(port):
            return True
        return False
#    Returns status of all currently running sensors
#
    
    
    def startSensors(self):
        for sense in self.sensorMap:
            sense = sensor.sensor(sense)
            sense.run()
    
    # Stops sensors and also runs get all data
    # this allows the threads to die
    def stopSensors(self):
        for sense in self.sensorMap:
            sense = sensor.sensor(sense)
            sense.update(0)
            logger.debug('Sensor ' + sense.port + ' stopping')
        return self.getAllData()

    def getData(self, port):
        if self.sensorMap.has_key(port):
            sense = sensor.sensor(self.sensorMap.get(port))
            return sense.collect()
        return None
    
    def getAllData(self):
        sensorData = []
        for sense in self.sensorMap:
            sense = sensor.sensor(sense)
            sensorData += [sense.collect()]
        return sensorData
#    Returns sensor data for each sensor
#
# all sensors handled within this module not single instances
#


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
            logger.debug('Sensor Thread init - ' + self.name)
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
