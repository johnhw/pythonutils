# import all of the relevant packages 

import sys,time,os,random,cPickle, math
import traceback
import numpy, scipy, scipy.signal
import pygame, thread
from shake import *              
from pygame.locals import *
import thread 
import config
                                                                  
        
        
class ShakeSkeleton:

      
    def print_stat(self, s, com):
            """Print out the state of the SHAKE device. This reads all of the basic settings from the device
            and prints them to standard output."""
           
            print "---==SHAKE details==---" 
            print "  => SHAKE No. [%s] on COM port %d" % (s.info_serial_number(),com)
            print "        HW revision %s" % (str(s.info_hardware_revision())[:4])
            print "        Firmware version %s" % (str(s.info_firmware_revision())[:4])                                   
            print "        at %d deg. C" % (s.read_temperature())
            power = s.read_power_status()[1]
            if power & SHAKE_EXT_POWER != 0:
                pwr_stat = "        On external power"
            else:
                pwr_stat = "        Battery at %d percent " % ((float(s.read_battery_level()[1]) / SHAKE_BATTERY_MAX)*100.0)
                
            if power & SHAKE_BAT_CHARGING !=0:
                pwr_stat = pwr_stat + " [charging]"
            if power & SHAKE_BAT_FULL !=0:
                pwr_stat = pwr_stat + " [CHARGED]"
            print pwr_stat
            print
            print "   => Settings"
            

            p = s.read_power_state()[1]
            for sensor in ((SHAKE_POWER_ACC, "Accelerometer"), (SHAKE_POWER_GYRO, "Gyroscope"), (SHAKE_POWER_VIB, "Vibrator"), (SHAKE_POWER_MAG, "Magnetometer"), (SHAKE_POWER_TEMP, "Temperature"), (SHAKE_POWER_ANALOG, "Analog"), (SHAKE_POWER_NAV, "Navigation switch")):
                
                if p & sensor[0]:
                    print "        %s  *ON*" % sensor[1]
                else:
                    print "        %s -off- " % sensor[1]
                
            
            print "         => Sample rates"
            for sensor in ((SHAKE_SENSOR_ACC, "Accelerometer"), (SHAKE_SENSOR_GYRO, "Gyroscope"), (SHAKE_SENSOR_MAG, "Magnetometer"), (SHAKE_SENSOR_HEADING, "Heading"), (SHAKE_SENSOR_CAP0, "Capacitive 0"), 
            (SHAKE_SENSOR_CAP1, "Capacitive 1"), (SHAKE_SENSOR_ANA0, "Analog 0"),  (SHAKE_SENSOR_ANA1, "Analog 1"),):
                filter = s.read_digital_filter(sensor[0])[1]
                
                if filter & 1 == 1:
                    fil = "Filtered"
                    if filter & 2 == 2:
                        fil = fil + " with min. phase filter"
                    else:
                        fil= fil + " with linear phase filter"                
                else:
                    fil = "Unfiltered"
                    
                print "            %s : sample rate %dHz [%s]" % (sensor[1], s.read_sample_rate(sensor[0])[1], fil)    
                
            if s.read_data_format()[1] & 2 == 2:
                data_format = "Raw (binary) mode"
            else:
                    data_format = "ASCII mode"
            
            print "         Data format %s" % (data_format)
            
            acc_mode = s.read_acc_config()[1]
            if acc_mode&1==0:
                print "         Accelerometer range +/- 2g",
            else:
                print "         Accelerometer range +/- 6g",
            
            if acc_mode&2==0:
                print "no highpass"
            else:
                print "highpass enabled"
            
            if s.read_calib_bypass()[1]!=0:
                print "         Calibration bypassed"
            else:
                print "         Calibration enabled"
                
            if s.read_cx_bypass()[1]!=0:            
                print "         Cross-axis bypassed"
            else:
                print "         Cross-axis calibration enabled"
                
            if s.read_packet_streaming()[1]==0:
                print "         Packet streaming mode"
            else:
                print "         Request mode"
     
            
            
            
            print 
            print
            
    def __init__(self, coms=(4,5), rate=100):
        """Specify the com ports for each shake (specify as many as you want), and the
        sampling rate in Hz"""
        
        self.shakes = []
    
        for com in coms:        
            s = shake_device()
            if type(com)==type(0):
                s.connect(com)
            else:
                s.connect_rfcomm(com)
            s.write_sample_rate(SHAKE_SENSOR_ACC, rate)
            s.write_sample_rate(SHAKE_SENSOR_GYRO, rate)
            s.write_sample_rate(SHAKE_SENSOR_MAG, rate)
                                    
            s.write_power_state(SHAKE_POWER_ACC | SHAKE_POWER_VIB | SHAKE_POWER_GYRO | SHAKE_POWER_MAG)
            
            # make sure accelerometer is in default configuration with binary mode
            s.write_acc_config(0)
            
            s.write_data_format(2)
            
            self.print_stat(s, com)
            self.shakes.append(s)
                               
                               
    def state(self):
        """Return the state of the sensors as a list of vectors (one vector for each shake)."""
        states = []
        for shake in self.shakes:
            #gyro and accelerometer
            state = shake.acc()
            
           
            state = state + shake.gyro()
            state = state + shake.mag()
            
            states.append(numpy.array(state))
        return states
            
    
        
        
# Skeleton class                                          
class Skeleton:
    
    # Initialise pygame, and load the fonts
    def init_pygame(self): 
        pygame.init()
        default_font_name = pygame.font.match_font('bitstreamverasansmono', 'verdana', 'sans')
        if not default_font_name:           
            self.default_font_name = pygame.font.get_default_font()  
        self.default_font = pygame.font.Font(default_font_name, 36)
        self.small_font = pygame.font.Font(default_font_name, 12)
        self.screen = pygame.display.set_mode((800,600))                  
        #store screen size
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
        
      
      
    #initialise any surfaces that are required
    def init_surfaces(self):        
        self.draw_buf = pygame.Surface(self.screen.get_size())    
        self.draw_buf.fill((255,255,255))
        
                           
    # init routine, sets up the engine, then enters the main loop
    def __init__(self):    
        self.init_pygame()
        self.init_surfaces()
        self.fps = 60
        
        self.shakes = ShakeSkeleton(coms=config.coms, rate=config.rate)
        
        self.clock = pygame.time.Clock()
        self.start_time = time.clock()
        self.main_loop()
    

    ### Frame loop. Called on every frame. All calculation should be carried out here     
    ### This is where the magic happens!
    def tick(self):          
          self.clock.tick(self.fps)                             
          self.handle_events()                   
          delta_t = time.clock() - self.start_time  
          self.start_time = time.clock()                  
          self.check_key_state()          
          self.flip()

                  
    # handles shutdown
    def quit(self):
        pygame.quit()        
        sys.exit(0)
        
    # wrapper for drawing text on screen
    def text(self, buffer, text,  color, position):       
        textImage = self.small_font.render(text, False, color)
        buffer.blit(textImage, position)
                     
        
    # this is the redraw code. Add drawing code between the "LOCK" and "END LOCK" sections
    def flip(self):
    
    
            
          self.screen.lock()
          #LOCK          
          self.screen.fill((255, 255, 255))          
          #END LOCK
          self.screen.unlock()                    
          
          states= self.shakes.state()
          y = 20
          
          ##### 
          ##### draw the current shake states ####          
          for state in states:
            self.text(self.screen, str(state), (0,0,0), (10, y))
            y += 30
          
          
          
          pygame.display.flip()
     
       
    # Get the array containing the up or down states for each key. For example, key_state[K_UP] is true if the up arrow key is pressed, [K_q] if Q is pressed, etc.
    def check_key_state(self):
          key_state = pygame.key.get_pressed()
          
            
           
          

   
    #returns last mouse position
    def get_mouse(self):
          return self.mouse_pos
     
    #Event handlers. These are called as events arrive
    def keydown(self,event):
          return
     
    def keyup(self,event):
          return
          
    def mouseup(self,event):
          return
     
    def mousedown(self,event):
          return
          
    def mousemove(self,event):
          (self.mouse_pos) = event.pos
          return
       
    
    #event handling code. Calls the relevant handlers
    def handle_events(self):
          for event in pygame.event.get():  
               if event.type==KEYDOWN:
                 
                    if event.key==K_ESCAPE:
                        self.quit()
                    else:
                        self.keydown(event)
                        
               if event.type==KEYUP:
                    self.keyup(event)
                    
               if event.type == QUIT:
                    self.quit()
               elif event.type == MOUSEBUTTONUP:
                    self.mouseup(event)
               elif event.type == MOUSEBUTTONDOWN:
                    self.mousedown(event)
               elif event.type == MOUSEMOTION:     
                    self.mousemove(event)


    #main loop. Just runs tick until the program exits     
    def main_loop(self):
        while 1:
            self.tick()
         
     
#Create and run the engine     
s = Skeleton()


          



 