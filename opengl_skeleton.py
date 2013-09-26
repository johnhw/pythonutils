import sys,time,os,random,cPickle, math
import traceback

import pygame, thread
from pygame.locals import *

import thread
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


            
                                              
                              
                                              

                                              
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
            throw(Exception("Invalid size for a ringbuffer: must be >2"))
          
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


    
    #initialize opengl with a simple ortho projection
    def init_opengl(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 500)
        glMatrixMode(GL_MODELVIEW)
        
        #enable texturing and alpha
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Initialise pygame, and load the fonts
    def init_pygame(self,w,h): 
        pygame.init()
        default_font_name = pygame.font.match_font('bitstreamverasansmono', 'verdana', 'sans')
        if not default_font_name:           
            self.default_font_name = pygame.font.get_default_font()  
        self.default_font = pygame.font.Font(default_font_name, 36)
        self.small_font = pygame.font.Font(default_font_name, 12)
        self.screen = pygame.display.set_mode((w,h) , pygame.OPENGL|pygame.DOUBLEBUF)                  
        #store screen size
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
        self.init_opengl()
       
      
    # create a display list for  a sprite   
    def create_sprite_list(texture, width, height):
        newList = glGenLists(1)
        glNewList(newList,GL_COMPILE);
        glBindTexture(GL_TEXTURE_2D, texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)    # Bottom Left Of The Texture and Quad
        glTexCoord2f(0, 1); glVertex2f(0, height)    # Top Left Of The Texture and Quad
        glTexCoord2f(1, 1); glVertex2f( width,  height)    # Top Right Of The Texture and Quad
        glTexCoord2f(1, 0); glVertex2f(width, 0)    # Bottom Right Of The Texture and Quad
        glEnd()
        glEndList()    
        return newList
    
    
    def del_sprite_list(list):
        glDeleteLists(list, 1)
   
    def del_texture(self, texture):
        glDeleteTextures(texture)
      
    # load a texture and return it
    def load_texture(self, fname):
        textureSurface = pygame.image.load(image)    
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)    
        width = textureSurface.get_width()
        height = textureSurface.get_height()    
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData )   
        return texture, width, height
        
        
    #initialise any surfaces that are required
    def init_surfaces(self):        
        pass
        
            

               
    # init routine, sets up the engine, then enters the main loop
    def __init__(self):    
        self.init_pygame(800,600)
        self.init_surfaces()
        self.fps = 60
        self.phase = 0
        self.clock = pygame.time.Clock()
        self.jitter_timer = JitterEstimator(10)               
        self.start_time = time.clock()
        self.main_loop()
        
    # handles shutdown
    def quit(self):
        pygame.quit()        
        sys.exit(0)
        
    # this is the redraw code. Add drawing code between the "LOCK" and "END LOCK" sections
    def flip(self):
          # clear the transformation matrix, and clear the screen too
          glMatrixMode(GL_MODELVIEW)
          glLoadIdentity()
          glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
          
          
          # simple drawing
          glColor4f(1.0,0.5,0.0,1.0)
          
          glTranslatef(self.w/2,self.h/2,-100)
          glRotatef(self.phase, 0, 1, 0)
          self.phase = self.phase+0.5
          
          glBegin(GL_TRIANGLES)
          glVertex3f(-50,-50,0)
          glVertex3f(50,-50,0)
          glVertex3f(0,50,0)
          glEnd()
          
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


          



 