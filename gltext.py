import sys,time,os,random,cPickle, math
import traceback

import pygame, thread
from pygame.locals import *
import thread
from OpenGL.GL import *
from OpenGL.GLU import *

# enter a 2d ortho drawing mode, with screen co-ordinates w,h
def begin_2d_mode(w,h):
        #switch to 2d
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0,  h, -1, 500)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        
# restore the projection and modelview matrices
def end_2d_mode():
        #restore perspective projection
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        

class GLText:
    def __init__(self, fontname, size, tex_w=None, tex_h=None):
        if tex_w:
            self.tex_w = tex_w
        else:
            self.tex_w = 512
        if tex_h:
            self.tex_h = tex_h
        else:
            self.tex_h = 128
        
        fname = pygame.font.match_font(fontname)
        self.surface = pygame.surface.Surface((self.tex_w, self.tex_h)).convert_alpha()
        self.surface.fill((0,0,0,0))
        
        self.tex = glGenTextures(1)
        textureData = pygame.image.tostring(self.surface, "RGBA", 1) 
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)        
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.tex_w, self.tex_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData )   
    
        self.font = pygame.font.Font(fname, size)
        
        
    def draw_text(self, string, unit_size=False):        
        surf = self.font.render(string, True, (255,255,255))
        textureData = pygame.image.tostring(surf, "RGBA", 1)    
        glBindTexture(GL_TEXTURE_2D, self.tex)
        w,h = surf.get_width(), surf.get_height()
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w,h, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        
        if unit_size:
            h = h/float(w)
            w = 1.0
        
        
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0,0.0)
        glVertex3f(0,0,0)
        glTexCoord2f(w/float(self.tex_w),0.0)
        glVertex3f(w,0,0)
        glTexCoord2f(w/float(self.tex_w),h/float(self.tex_h))
        glVertex3f(w,h,0)
        glTexCoord2f(0,h/float(self.tex_h))
        glVertex3f(0,h,0)        
        glEnd()
        
        
        return (surf.get_width(), surf.get_height())
       
    
    def text_3d(self, string):
        w,h = self.draw_text(string, unit_size=True)
        return (w,h)
        
    def text_on_3d(self, string, x,y,z, screen_w, screen_h):
        x,y,z = gluProject(x,y,z)
        begin_2d_mode(screen_w,screen_h)
        glTranslatef(x,y,0)
        w,h = self.draw_text(string)
        end_2d_mode()
        return (w,h)
        
        
    def text_2d(self, string, x, y):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(x,y,0)
        w,h = self.draw_text(string)
        glPopMatrix()
        return (w,h)
        
