import sys,time,os,random,cPickle, math
import traceback

import pygame, thread
from pygame.locals import *
import Numeric
import thread                                                                                 
                                              
#util classes for estimating FPS and std. dev. of FPS
class JitterEstimator:
    def __init__(self, samples):
        self.buffer = Ringbuffer(samples)
        
    def new_sample(self, delta_t):
        self.buffer.new_sample(delta_t)
        
    def get_state(self):
        samples = self.buffer.get_samples()
        length = self.buffer.get_length()        
        sum = 0
        for s in samples:
            sum = sum + s
        mean = sum / length
        dev = 0
        for s in samples:
            dev = dev + (s - mean) * (s-mean)
        dev = dev / length
        return (mean, math.sqrt(dev))

class Ringbuffer:
    def __init__(self, size):
        if size<2:
            throw(Exception("Invalid size for a ringbuffer: must be >=2"))
          
        self.n_samples = size        
        self.samples = [0] * size
        self.read_head = 1
        self.write_head = 0
        
    def get_length(self):
        return self.n_samples
        
    def get_samples(self):
        return self.samples
        
    def new_sample(self, x):
        self.samples[self.write_head] = x
        self.read_head += 1
        self.write_head += 1
        self.read_head %= self.n_samples
        self.write_head %= self.n_samples
    
        
        
        
        
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
        
    # simple iso projection from 3d to 2d.
    def isometric_project(x,y,z):
        xp = (x-z)
        yp = ((x+z)>>1) - y
        return (xp, yp)
            

               
    # init routine, sets up the engine, then enters the main loop
    def __init__(self):    
        self.init_pygame()
        self.init_surfaces()
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.jitter_timer = JitterEstimator(10)               
        self.start_time = time.clock()
        self.main_loop()
        
    # handles shutdown
    def quit(self):
        pygame.quit()        
        sys.exit(0)
        
    # wrapper for drawing text on screen
    def text(self, buffer, text,  color, position):       
        textImage = self.small_font.render(text, False, color)
        buffer.blit(textImage, position)
                     
    # draw the fps, and the std. dev. of the fps
    def draw_stats(self):
          (mean, std) = self.jitter_timer.get_state()
          self.text(self.screen, "FPS: %.1f Jitter: %.1f" % (mean, std) , (0,100,255), (40, 10))
        
    # this is the redraw code. Add drawing code between the "LOCK" and "END LOCK" sections
    def flip(self):
    
          self.screen.lock()
          #LOCK
          
          self.screen.fill((255, 255, 255))
          
          
          #END LOCK
          self.screen.unlock()          
          self.draw_stats()
          pygame.display.flip()
     
       
    # Get the array containing the up or down states for each key. For example, key_state[K_UP] is true if the up arrow key is pressed, [K_q] if Q is pressed, etc.
    def check_key_state(self):
          key_state = pygame.key.get_pressed()
          
            
           
    #frame loop. Called on every frame. all calculation shpuld be carried out here     
    def tick(self):          
          self.clock.tick(self.fps)                             
          self.handle_events()                   
          delta_t = time.clock() - self.start_time  
          self.jitter_timer.new_sample(1.0/delta_t)
          self.start_time = time.clock()                  
          self.check_key_state()          
          self.flip()

          
          

   
    #returns last mouse position
    def get_mouse(self):
          return self.mouse_pos
     
    #Event handlers. These are called as events arrive
    def keydown(self,event):
          return
     
    def keyup(self,event):
          if event.key == K_ESCAPE:
               self.quit()
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


          



 