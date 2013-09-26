import skeleton, pygame
from vector import *
from pygame.locals import *


class Polyeditor:
    def __init__(self, polys=[], krange=(-100, 100)):
        self.polys = polys        
        self.control_width = 6        
        self.range = krange   
        
    
    
    def main_loop(self):
    
    
        self.skeleton = skeleton.Skeleton(draw_fn=self.draw,tick_fn=self.tick,event_fn=self.event)        
        fullrange = self.range[1] - self.range[0]
        self.xscale = float(self.skeleton.w)/fullrange
        self.yscale = float(self.skeleton.h)/fullrange
        self.xoffset = (self.range[0]+self.range[1])/2
        self.yoffset = (self.range[0]+self.range[1])/2
        self.in_drawing = False
        self.drag_pt = None
        self.drag_poly = None

        
        self.skeleton.main_loop()
        del self.skeleton 
        
    def tick(self, dt):
        
        if self.drag_poly!=None:
            self.polys[self.drag_poly][self.drag_pt] = self.untransform(pygame.mouse.get_pos())
        
        
    def inside(self, pt):
        
        for k,poly in enumerate(self.polys):
            for i, test_pt in enumerate(poly):               
                if vdistance(pt,test_pt)<self.control_width*4:                    
                    return  k,i
                    
        return None
        
    
    def mousedown(self, event):    
        pt = self.inside(self.untransform(event.pos))
        
        
        if pt==None or self.in_drawing:
            self.drag_pt = -1
            self.drag_poly = -1
            if event.button==1:
                if not self.in_drawing:
                    self.polys.append([self.untransform(event.pos)])                           
                self.polys[-1].append(self.untransform(event.pos))
                self.in_drawing=True
            if event.button==3:                             
                    
               self.drag_pt = None
               self.drag_poly = None
               self.in_drawing = False
               
        else:
             if event.button==1:                
                 self.drag_poly = pt[0]
                 self.drag_pt = pt[1]
             else:                
                  del self.polys[pt[0]][pt[1]]
            
    def mouseup(self, event):
        
        if not self.in_drawing:
             self.drag_pt = None
             self.drag_poly = None
            
        
    def event(self, event):
         if event.type == MOUSEBUTTONUP:
                self.mouseup(event)
         if event.type == MOUSEBUTTONDOWN:
                self.mousedown(event)
      
              
    def transform(self,pt):
        return ((pt[0]-self.xoffset) *self.xscale+self.skeleton.centre_x, 
                (pt[1]-self.yoffset) *self.yscale+self.skeleton.centre_y)
        
    def untransform(self,pt):
        return (((pt[0]-self.skeleton.centre_x)/float(self.xscale))+self.xoffset, 
                ((pt[1]-self.skeleton.centre_y)/float(self.yscale))+self.yoffset)
    
    
    def get_closed_polys(self):
        polys = []
        for poly in self.polys:
            polys.append(poly.append(poly[0]))
        return polys
        
   
    def draw(self, surface):
        surface.fill((0,0,0))
        for poly in self.polys:
            for pt in poly:
                pygame.draw.circle(surface, (255,255,255), self.transform(pt), self.control_width,1)
            if len(poly)>1:
                pygame.draw.aalines(surface, (128,128,128), True, map(self.transform, poly))
               


               
if __name__=="__main__":
    p = Polyeditor()
    p.main_loop()
    