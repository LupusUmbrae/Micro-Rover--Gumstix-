#Rover Unique Details
RID = '001'

#logging
logging_level = 'info'
LOG_FILENAME = 'log.out'


#Connection details
host_ip = '10.42.43.1ge'
host_port = 61613
queue_commands = '/topic/commands'
queue_sensors = '/topic/sense'
queue_log = '/topic/log'

#sensor details

#sensor number followed by interval in seconds, set interval to 0 to not check sensor.

sensors_enabled = False
sensors_config = [#number, name, interval, type
           [0, 'sensor1', 3, 'default'],
           [0, 'sensor2', 0, 'default'],
           [0, 'sensor3', 0, 'default']
           ]

# Port [number, name, interval, type]
sensorsConfig = {
                 0: [0, 'sensor1', 3, 'default'],
                 1: [0, 'sensor2', 0, 'default'],
                 2: [0, 'sensor3', 0, 'default']
                 }

sensors_collect = 9 # Rate to send data back (seconds)

#motors details
wheel_base = 60
max_angle = 50
half_length = 50

servo_dif = 0.5
servo_mid = 1.5

diff_inc = 10


#camera details