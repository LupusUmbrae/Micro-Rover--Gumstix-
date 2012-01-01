import logging
import driver
logger = logging.getLogger('gumstix.motors.motor')

class motor():
    def __init__(self, number, servoMid, servoDif):
        global pwm, driver
        self.no = number #used to reference which motor
        self.mid = servoMid
        self.dif = servoDif
        pwm = driver.pwm_driver(self.no, 1, 50)
        logger.debug('Motor' + str(self.no) + ' Connected to driver')
        
    
    def getSpeed(self, speed):
        value = pwm.read_speed()
        
    
    def setSpeed(self, speed):
        logger.debug('Update Command:' 
                     + '\n \t Motor: \t' + str(self.no) 
                     + '\n \t Speed: \t' + str(speed))
        
        speed = (float(speed)/100)*self.dif
        freq = int(((self.mid + speed)/1000)**(-1))
        
        
        logger.debug('Update Frequency:' 
                     + '\n \t Motor: \t' + str(self.no) 
                     + '\n \t Frequency: \t' + str(freq))
        pwm.update_pulsewidth(freq)