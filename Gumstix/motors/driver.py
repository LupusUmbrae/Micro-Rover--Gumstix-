# OMAP3503 GP_TIMER PWM DRIVER
# Class to configure OMAP3503
# general purpose timers 8,9,10,11
# for PWM signal generation as well
# as update frequencies

import mmap, os, sys

import logging
logger = logging.getLogger('gumstix.motors.driver')

def setup_pwm():
    
    MAP_SIZE = 4096
    MAP_MASK = MAP_SIZE - 1
    f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
    
    logger.info('Configuring PWM Mux')
    
    #PWM for GPIO 8, 11
    logger.debug('Configuring MUX for GPT 11, 8')
    addr = 0x48002178
    m = mmap.mmap(f, MAP_SIZE, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=addr & ~MAP_MASK)
    m.seek(addr & MAP_MASK)
    m.write('\x02\x01') #gpt11,8_MUX, Turn on PWM
    m.close()

    logger.debug('Configuring MUX for GPT 10, 9')
    #PWM for GPIO 9, 10
    addr = 0x48002174
    m = mmap.mmap(f, MAP_SIZE, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=addr & ~MAP_MASK)
    m.seek(addr & MAP_MASK)
    m.write('\x02\x01') #gpt10,9_MUX, Turn on PWM
    m.close()
    os.close(f)

class pwm_driver():
    def __init__(self, number, mode, timer_freq):
        #Select timer
        if number == 1:
            self.startAddr = str(0x4903e000)
        elif number == 2:
            self.startAddr = str(0x49040000)
        elif number == 3:
            self.startAddr = str(0x48086000)
        elif number == 4:
            self.startAddr = str(0x48088000)
        else:
            pass #wrong input
        
        #Offsets, TI OMAP35xx technical reference manual
        self.TIOCP_CFG = str(0x010)
        self.TISTAT = str(0X014)
        self.TISR = str(0x018)
        self.TIER = str(0x01c)
        self.TWER = str(0x020)
        self.TCLR = str(0x024)
        self.TCRR = str(0x028)
        self.TLDR = str(0x02c)
        self.TTGR = str(0x030)
        self.TWPS = str(0x034)
        self.TMAR = str(0x038)
        self.TCAR1 = str(0x03c)
        self.TSICR = str(0x040)
        self.TCAR2 = str(0x044)
        self.TPIR = str(0x048)
        self.TNIR = str(0x04c)
        self.TCVR = str(0x050)
        self.TOCR = str(0x054)
        self.TOWR = str(0x058)
        
        #Pre-defined writes
        self.MAP_SIZE = 4096
        self.MAP_MASK = self.MAP_SIZE - 1
        self.stop = '00000000'
        self.start = '00001843'
        self.update_cycles(timer_freq)
        logger.debug('Driver initiated for motor: \t ' + str(number))


    def read(self, addr): #Not in use, yet
        f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        m = mmap.mmap(f, self.MAP_SIZE, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=int(addr, 16) & ~self.MAP_MASK)
        m.seek(int(addr, 16) & self.MAP_MASK)
        c = m.read(4)
        value = value.replace("0x", "").replace("/x", "").replace(" ", "") # strip 0x, /x, spaces
        value = value[6:8]+value[4:6]+value[2:4]+value[0:2] # re order
        m.close
        os.close(f)
        logger.debug('Read:' +
                     '\n\t Hex Value \t ' + str(value) +
                     '\n\t Address: \t ' + str(addr))
        return value
    
    def write(self, addr, value):#Feedback needed
        f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        m = mmap.mmap(f, self.MAP_SIZE, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=int(addr, 16) & ~self.MAP_MASK)

        m.seek(int(addr, 16) & self.MAP_MASK)
        # Re-Arrange values into backwards pairs, decode converts the '\\x' to and escape string
        value = (('\\x' + value[6:8]).decode('string_escape') + 
                 ('\\x' + value[4:6]).decode('string_escape') + 
                 ('\\x' + value[2:4]).decode('string_escape') + 
                 ('\\x' + value[0:2]).decode('string_escape'))
        logger.debug('Written:' +
                     '\n\t Hex Value \t ' + str(value.encode('string_escape')) +
                     '\n\t Address: \t ' + str(addr))

        m.write(value)
        m.close
        os.close(f)
       
    def addrOffset(self, offset):
        addr = hex(int(self.startAddr) + int(offset)).replace("0x", "").replace("L", "")
        logger.debug('Offset Address: \t ' + str(addr))
        return addr
    
    def strToHex(self, string):
        value = hex(string).replace("0x", "").replace("L", "")
        logger.debug('String -> Hex: \t ' + str(value))
        return value
    
    def hexToStr(self, hex):
        value = int(hex, 16).replace("L", "")
        logger.debug('Hex -> String: \t ' + str(value))
        return value
    
    def steps(self, freq):
        if(freq > 32000):
            return #frequency to high
        steps = int( (1/float(freq)) / (1/float(32000)) )#Number of 32KHz cycles into given frequency cycle
        logger.debug('Steps: \t ' + str(steps))
        return steps

    def freq_cycles(self, freq):
        steps = self.steps(freq)
        value = 4294967295 - steps
        self.load = value
        logger.debug('Cycles Frequency: \t ' + str(value))
        return self.strToHex(value)
    
    def freq_pulsewidth(self,freq):
        steps = self.steps(freq)
        value = self.load + steps
        logger.debug('Pulse Width Frequency \t ' + str(value))
        return self.strToHex(value)

    
    #Start of callable functions
    def update_cycles(self, freq): # Changes timer
        self.stop_motors() 
        
        #Calculate hex for timer cycles and update timer load
        value = self.freq_cycles(freq)
        addr = self.addrOffset(self.TLDR)
        logger.info('Cycles Update:'
                    + '\n\t Frequency: \t ' + str(value)
                    + '\n\t Address: \t ' + str(addr))
        self.write(addr, value)
        
        #Reset timer counter
        value = 'ffffffff'
        addr = self.addrOffset(self.TCRR)
        logger.debug('Pulse Width Update'
                    + '\n\t Frequency: \t ' + str(value)
                    + '\n\t Address: \t ' + str(addr))
        self.write(addr, value)
        
        self.start_motors()
    
    def update_pulsewidth(self, freq): # Changes the control pulse width on the timer
        self.stop_motors()
        
        #Calculate Hex for frequency and update timer match
        value = self.freq_pulsewidth(freq)
        addr = self.addrOffset(self.TMAR)
        logger.info('Pulse Width Update'
                    + '\n\t Frequency: \t ' + str(value)
                    + '\n\t Address: \t ' + str(addr))
        self.write(addr, value)
        
        #Reset timer counter
        value = 'ffffffff'
        addr = self.addrOffset(self.TCRR)
        logger.info('Pulse Width Update'
                    + '\n\t Frequency: \t ' + str(value)
                    + '\n\t Address: \t ' + str(addr))
        self.write(addr, value)
        self.start_motors()
    
    def read_speed(self):
        addr = self.addrOffset(self.TMAR)
        value = self.read(addr)
        freq = self.hexToStr(value)
        logger.info('Pulse Width Read'
                    + '\n\t Hex: \t ' + str(value)
                    + '\n\t Frequency: \t ' + str(freq)
                    + '\n\t Address: \t ' + str(addr))
        return value
            
    def start_motors(self): # Starts PWM on timer
        addr = self.addrOffset(self.TCLR)
        self.write(addr, self.start)
    
    def stop_motors(self): # Stops Timer
        addr = self.addrOffset(self.TCLR)
        self.write(addr, self.stop)
        

    