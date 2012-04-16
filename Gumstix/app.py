# Import Logging
import logging # used for logging errors
import logging.handlers

import ConfigParser
import ast

#import packages
import threading
import sys
import Queue

import stomp # Can be installed

import camera # Not in use

from comms import message_controls
from motors import motor_controls
from sensors import sensorControl

#Grab all the config variables



# Read config file
config = ConfigParser.RawConfigParser()
config.read('config.cfg')

#Setup Logging
logfile = logging.FileHandler(config.get('logging', 'logFilename'))
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
level = LEVELS.get(config.get('logging', 'loggingLevel'), logging.NOTSET)
logging.basicConfig(level=level)
logger = logging.getLogger('gumstix.app')
logger.info('Logging Started')

# Parse some of the config data to local variables
RID = config.getint('rover', 'RID')
hostIp = config.get('connection', 'hostIp')
hostPort = config.getint('connection', 'hostPort')
queueCommands = config.get('connection', 'queueCommands')
queueSensors = config.get('connection', 'queueSensors')
queueLog = config.get('connection', 'queueLog')

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
    conn = stomp.Connection([(hostIp, hostPort)]) # Who to connect to
    conn.set_listener('', Listener()) # Rover specific listener 
    conn.start()
    conn.connect(wait=True)
    conn.subscribe(destination=queueCommands, ack='auto') # Auto get commands
    
    ##Setup motors class
    logger.info('Configuring Motors')
    motors = motor_controls(config.get('motors', 'wheelBase'), 
                            config.get('motors', 'maxAngle'), 
                            config.get('motors', 'halfLength'), 
                            config.get('motors', 'diffInc'), 
                            config.get('motors', 'servoMid'), 
                            config.get('motors', 'servoDif'))
    
    
    ##Setup sensor threads 
    if config.getboolean('sensors', 'enabled'):
        logger.info('Configuring Sensors')
        sensorControl(ast.literal_eval(config.get('sensors', 'config')))
        # Start data collection timer
        st = threading.Timer(config.get('sensors', 'timer'), sensors_data_collect(config.get('sensors', 'timer')))
        st.start()
    
    
    ##Loop through other processes
    while run:
        try: ##Handle Command Queue
            command = commandQ.get(0)
            command_handle(command)
            commandQ.task_done()            
        except Queue.Empty:
            pass
        
            
        
        
    conn.send("Rover '%s' Disconnecting" % RID, destination=queueLog)
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
            conn.send(errorMessage, destination=queueLog)
                
    except KeyError:
        logger.error('Command Error \t Key Error')
        conn.send("Command - Key Error:", destination=queueLog)
    except TypeError:
        logger.error('Command Error \t Type Error')   
        conn.send("Command - Type Error:", destination=queueLog) 

def sensors_data_collect(sensors_collect):    
    message = sensorControl.getAllData(self)
    logger.info('Message Compiled from sensors \n \t' + str(message))
    m = message_controls('sensor_data', message)
    message = m.serialize()
    conn.send(message, destination=queueSensors)
    st = threading.Timer(sensors_collect, sensors_data_collect)
    st.start()

class Listener(stomp.ConnectionListener):


    def on_connecting(self, host_and_port):
        print 'connection %s %s' % host_and_port
        
    def on_connected(self, headers, body):
        #Send message to epc
        conn.send("Rover '%s' Connected" % RID, destination=queueLog) 

    def on_disconnected(self):
        pass
    
    def on_receipt(self, headers, body):
        pass

    def on_error(self, headers, body):
        errorMessage = 'STOMP ERROR: %s' %body 
        conn.send(errorMessage, destination=queueLog)  
    
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
            conn.send("STOMP Message - Key Error: ", destination=queueLog)
        except TypeError:
            logger.error('Message Error \t Type Error')   
            conn.send("STOMP Message - Type Error: ", destination=queueLog)  
             

if __name__ == '__main__':
    start()