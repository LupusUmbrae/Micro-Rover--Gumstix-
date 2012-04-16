# Import Logging
import logging # used for logging errors
import logging.handlers



#import packages
import threading
import sys
import Queue

import stomp # Can be installed

import camera # Not in use

from comms import message_controls
from motors import *
from sensors import *

#Grab all the config variables
from config import *
from sensors.controls import sensorControl


#Setup Logging
logfile = logging.FileHandler(LOG_FILENAME)
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
level = LEVELS.get(logging_level, logging.NOTSET)
logging.basicConfig(level=level)
logger = logging.getLogger('gumstix.app')
logger.info('Logging Started')

def start():
    print '####################'
    print '# GUMSTIX MAIN APP #'
    print '####################'
    global conn
    global motors
    global run
    global sensorControl
    global commandQ
    run = True

    ##Start Queues for commands
    commandQ = Queue.Queue()   

    ##Start stomp connection
    logger.info('Starting Stomp')
    conn = stomp.Connection([(host_ip, host_port)]) # Who to connect to
    conn.set_listener('', Listener()) # Rover specific listener 
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(destination=queue_commands, ack='auto') # Auto get commands
    
    ##Setup motors class
    logger.info('Configuring Motors')
    motors = motor_controls(wheel_base, max_angle, half_length, diff_inc, servo_mid, servo_dif)
    
    
    ##Setup sensor threads 
    if sensors_enabled:
        logger.info('Configuring Sensors')
        sensorControl(sensorsConfig)
        # Start data collection timer
        st = threading.Timer(sensors_collect, sensors_data_collect)
        st.start()
    
    
    ##Loop through other processes
    while run:
        try: ##Handle Command Queue
            command = commandQ.get(0)
            command_handle(command)
            commandQ.task_done()            
        except Queue.Empty:
            pass
        
            
        
        
    conn.send("Rover '%s' Disconnecting" % RID, destination=queue_log)
    st.stop()
    conn.disconnect()

def command_handle(command):
    try:
        parametersArray = command.getParams()
        functionName = command.getFunctionName()
                
        ##What command is it?
        logger.info('Command Received' 
                    + '\n \t Function \t' + str(functionName)
                    + '\n \t Parameters \t' + str(parametersArray))
        if functionName == 'move':
            logger.debug('Move Command' 
                         + '\n \t Speed \t' + str(parametersArray[1])
                         + '\n \t Angle \t' + str(parametersArray[0]))
            motors.move(parametersArray[0], parametersArray[1])
                    
        elif functionName == 'sensor':
            logger.debug('Sensor Command' 
                         + 'Parameters' + str(parametersArray))
                
        elif functionName == 'stop':
            run = False
                    
        else:
            logger.warning('Unrecognised command \t' + str(functionName))
            errorMessage = "Command Not Recognised: %s" % functionName
            conn.send(errorMessage, destination=queue_log)
                
    except KeyError:
        logger.error('Command Error \t Key Error')
        conn.send("Command - Key Error:", destination=queue_log)
    except TypeError:
        logger.error('Command Error \t Type Error')   
        conn.send("Command - Type Error:", destination=queue_log) 

def sensors_data_collect():    
    message = sensorControl.getAllData(self)
    logger.info('Message Compiled from sensors \n \t' + str(message))
    m = message_controls('sensor_data', message)
    message = m.serialize()
    conn.send(message, destination=queue_sensors)
    st = threading.Timer(sensors_collect, sensors_data_collect)
    st.start()

class Listener(stomp.ConnectionListener):


    def on_connecting(self, host_and_port):
        print 'connection %s %s' % host_and_port
        
    def on_connected(self, headers, body):
        #Send message to epc
        conn.send("Rover '%s' Connected" % RID, destination=queue_log) 

    def on_disconnected(self):
        pass
    
    def on_receipt(self, headers, body):
        pass

    def on_error(self, headers, body):
        errorMessage = 'STOMP ERROR: %s' %body 
        conn.send(errorMessage, destination=queue_log)  
    
    def on_send(self, headers, body):
        pass

    def on_message(self, headers, body):
        try: #prevents the stomp loop failing on error
            message = message_controls.unserialize(body)
            
            logger.info('Message Received')
            
            try:
                commandQ.put(message,0)
                logger.info('Message added to Command Queue')
            except Queue.Full: #Should not occur, queue is infinite
                logger.warning("Command Queue full, message lost")     
                           
        except KeyError:
            logger.error('Message Error \t Key Error')
            conn.send("STOMP Message - Key Error: ", destination=queue_log)
        except TypeError:
            logger.error('Message Error \t Type Error')   
            conn.send("STOMP Message - Type Error: ", destination=queue_log)  
             

if __name__ == '__main__':
    start()