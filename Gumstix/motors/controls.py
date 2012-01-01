
## Motor control class
##-------------------- 
## This class provides all the tools
## needed to control the motion of the rover
import logging
logger = logging.getLogger('gumstix.motors.controls')
from math import pi, tan, radians

class motor_controls():
    def __init__(self, wheelBase, maxAngle, halfLength, increment, motors):
        self.wheelBase = wheelBase
        self.increment = increment
        self.maxAngle = maxAngle
        self.halfLength = halfLength
        self.currentDifferential = 0 #start rover in straight line
        self.angle = 0 #start rover in straight line
        logger.debug('Timers configured for PWM')
        self.motor1 = motors[0] # Front Left
        self.motor2 = motors[1] # Front Right
        self.motor3 = motors[2] # Back Left
        self.motor4 = motors[3] # Back Right
        logger.debug('Motor Settings:' 
                     + '\n\t Wheelbase \t' + str(self.wheelBase) 
                     + '\n\t Increment \t' + str(self.increment) 
                     + '\n\t Current Diff \t' + str(self.currentDifferential) 
                     + '\n\t Current Angle \t' + str(self.angle))
        
    def move(self, angle, speed):
        # Calls to this function only
                
        #check inputs
        speed = int(speed)
        angle = int(angle)
        if (speed <= 100) and (speed >= -100):
            if (angle <= 100) and (angle >= -100):
                logger.info('Changing Motors to;' 
                             + '\n\t Speed \t' + str(speed) 
                             + '\n\t Angle \t' + str(angle))
                self.calcDiff(angle,speed)
            else:
                logger.error('Incorrect Angle Supplied ' + str(angle))
                #angle error
                pass
        else:
            logger.error('Incorrect speed given ' + str(speed))
        #speed error
        
    
    def calcDiff(self, angle, speed):
        self.angle = int((float(self.maxAngle)/100)*angle)
        logger.debug('self.angle \t' + str(self.angle))
        self.speed = speed
        logger.debug('self.speed \t' + str(self.speed))
        halfAngle = angle/2
        logger.debug('Half Angle \t' + str(halfAngle))
        if self.angle < 0:
            halfAngle = halfAngle * -1
            logger.debug('Half Angle \t' + str(halfAngle))
        # Calculate required differential
        innerRadius = 2*pi* (tan(radians(halfAngle/2))*self.halfLength)
        logger.debug('Inner Radius \t' + str(innerRadius))
        outerRadius = (2*pi* (tan(radians(halfAngle/2))*self.halfLength)) + self.wheelBase
        logger.debug('Outer Radius \t' + str(outerRadius))
        differential = innerRadius/outerRadius
        logger.debug('Differential \t' + str(differential))
        if self.angle < 0:
            differential = -differential
            logger.debug('Differential \t' + str(differential))
        
        
        #Increment angle gradually and update using
        #updateSpeed class
        if self.currentDifferential != differential:
            while self.currentDifferential != differential:
                #update differential
                if (self.currentDifferential - differential) > self.increment:
                    self.currentDifferential = self.currentDifferential - self.increment
                elif (self.currentDifferential - differential) < -self.increment:
                    self.currentDifferential = self.currentDifferential + self.increment
                else:
                    self.currentDifferential = differential
                    
                self.updateSpeed(self.currentDifferential, self.speed) # Update motor speeds
                logger.debug('Motors Set to' 
                            + '\n\t Speed \t' + str(self.speed) 
                            + '\n\t Angle \t' + str(self.angle))
        else:
            self.updateSpeed(self.currentDifferential, self.speed) # Update motor speeds
            logger.debug('Motors Set to' 
                            + '\n\t Speed \t' + str(self.speed) 
                            + '\n\t Angle \t' + str(self.angle))                   
       
        
    
    def updateSpeed(self, diff, speed):
        if diff < 0: # Turning left
            m1 = speed
            m2 = speed + (speed * diff)
            m3 = speed
            m4 = speed + (speed * diff)
        elif diff > 0: # Turning Right
            m1 = speed - (speed * diff)
            m2 = speed
            m3 = speed - (speed * diff)            
            m4 = speed
        else: # Straight Forward
            m1 = speed
            m2 = speed
            m3 = speed
            m4 = speed         
        
        # Update through motor class               
        self.motor1.setSpeed(m1)
        self.motor2.setSpeed(m2)
        self.motor3.setSpeed(m3)
        self.motor4.setSpeed(m4)
        logger.debug('Motor Speeds: '
                     + '\n\t Motor 1: \t' + str(m1)
                     + '\n\t Motor 2: \t' + str(m2)
                     + '\n\t Motor 3: \t' + str(m3)
                     + '\n\t Motor 4: \t' + str(m4))
        
        
    
    def getStatus(self, motor):
        #get motor speed 
        m1speed = self.motor1.getSpeed()
        m2speed = self.motor2.getSpeed()
        m3speed = self.motor3.getSpeed()
        m4speed = self.motor4.getSpeed()
        return [self.currentDifferential, self.angle, m1speed, m2speed, m3speed, m4speed]
        