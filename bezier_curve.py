import skeleton
import math
import pygame, time
from vector import *


def bezier_surface_split(pts, updown=False,  size=5, proj_fn=None):

    b1 = []
    b2 = []
            
    test_pts =[pts[0], pts[3], pts[15], pts[12]]
    if proj_fn:        
        test_pts = proj_fn(test_pts)
    
    # stop if size of quad<size
    v1 = vdistance(test_pts[0], test_pts[2])
    v2 = vdistance(test_pts[1], test_pts[3])
    
    # return quad
    if v1<size and v2<size:    

        n1 = vnormalize(vsub(pts[0][0:3], pts[3][0:3]))
        n2 = vnormalize(vsub(pts[0][0:3], pts[12][0:3]))        
        normal = vcross3(n1,n2)        
        return [test_pts+normal]
        
    
    if updown:  
        # up down division
        for i in range(4):
            segment = []
            for j in range(4):
                segment.append(pts[j*4+i])            
            u,d = divide_bezier(segment, at=0.5)
            b1 = b1 + u 
            b2 = b2 + d
            
    else:
        # left right division
        for i in range(4):            
            segment = pts[i*4:(i+1)*4]
            l,r = divide_bezier(segment,at=0.5)
            b1 = b1 + l 
            b2 = b2 + r
            
    return bezier_surface_split(b1, not updown,size=size, proj_fn=proj_fn) + bezier_surface_split(b2,not updown, size=size, proj_fn=proj_fn)
    
            
            
            
def divide_bezier(segment, at):
    vs = [segment]
    split = segment
    while len(split)>1:
        split = vector_split(split, at)
        vs.append(split)
        
    bez1 = [v[0] for v in vs]
    bez2 = [v[-1] for v in vs]
    bez2.reverse()    
    
    return bez1, bez2
    
    
def vweight_div(vec):
    return vscale(vec[0:-1], 1.0/vec[-1])
    
    
def isflat(segment, tol):
    ab = vsub(a,b)
    ac = vsub(a,c)
    ad = vsub(a,d)
    
    m1 = vdotproduct(ab,ad)
    m2 = vdotproduct(ac,ad)
    
    return abs(1-m1)<tol and abs(1-m2)<tol

    
    
def decasteljau_split(segment, tol, weighted=False):         



    if not weighted:
        a,b,c,d = segment[0],segment[1],segment[2],segment[3]
    else:
        a,b,c,d = map(vweight_div, [segment[0],segment[1],segment[2],segment[3]])
        
        
    if isflat(segment, tol):
        return [segment[0], segment[-1]]
    
    bez1, bez2 = divide_bezier(segment, at=0.5)
            
    return decasteljau_split(bez1, tol, weighted)+decasteljau_split(bez2, tol, weighted)
    
    
def render_bezier(segment, tol=1e-5):
    return decasteljau_split(segment, tol, weighted=False)    
    
    
def preweight(segment):
    new_segment = []
    for pt in segment:
        w = pt[-1]
        scaled = vscale(pt[0:-1], w)
        pt = scaled+[w]
        new_segment.append(pt)
    return new_segment
    
    
def postweight(pts):
    proj_pts = []    
    for pt in pts:        
        w = pt[-1]        
        proj_pts.append(vscale(pt[0:-1], 1.0/w))                
    return proj_pts
    
    
def weighted_render(segment, tol=1e-5):
           
    return  postweight(decasteljau_split(preweight(segment), tol, weighted=True))
    
    
        
 


    
class BezierPath:
    def __init__(self, initial_segment):
        if len(initial_segment)==2:
            # line, so expand
            mid1 = vadd(vscale(initial_segment[0], 0.75), vscale(initial_segment[1],0.25))
            mid2 = vadd(vscale(initial_segment[0], 0.25), vscale(initial_segment[1],0.75))            
            initial_segment=[initial_segment[0],mid1, mid2, initial_segment[1]]
        self.segments = []
        
    def add_segment(self, side="right"):
        pass
        
        
        
        
        
class BezierTest:
    def __init__(self):
        self.skeleton = skeleton.Skeleton(tick_fn=self.tick, draw_fn=self.draw)
        self.segment = [[200,50,1], [20, 300,2] , [200, 350,1], [10, 500,1]]
        self.skeleton.main_loop()
        
        
        
    def tick(self, dt):
        
        
        pass
        
    def draw(self, surface):        
        surface.fill((0,0,0))
        
        
        pts = weighted_render(self.segment, 1e-3)         
        
        for i in range(80):
        
            newpts = []
            for pt in pts:
                newpts.append(((pt[0]-200)*math.sin((i/float(80))*math.pi*2)+200, pt[1]))
            pygame.draw.aalines(surface, (255,128,0), False, newpts)        
            
        for pt in pts:
            d = abs(200-pt[0])+1
            d = d 
            pygame.draw.ellipse(surface, (255,128,0), (200-d, pt[1]-25,d*2 , 50),1)
        
        for pt in self.segment:
            pt = pt[0:-1]            
            pygame.draw.circle(surface, (0,0,0), pt, 5)
            
            
            
        
        
        
    
        
if __name__=="__main__":    
    
    
    g = BezierTest()
    
    