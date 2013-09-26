
import math
import bezier_curve

try: 
   import pygame
except:
    print "No pygame..."
        
                

                
def aacircle_pts(pos, radius,  start_angle=0, end_angle=2*math.pi, steps=32):
    out_pts = []    
    
    angles = []
    
    # get start and end points
    istart = (start_angle/(2*math.pi)) * steps
    iend = (end_angle/(2*math.pi)) * steps
    
    if iend<istart:
        iend, istart = istart, iend
        
    # compute angles
    angles.append(start_angle)
    for i in range(iend-istart):
        a = (i/float(steps)) * math.pi * 2 + start_angle
        angles.append(a)
    angles.append(end_angle)    
    
    # store the points
    for angle in angles:            
        out_pts.append((math.cos(angle)*radius+pos[0],
        -math.sin(angle)*radius+pos[1]))
        
        
    return out_pts
    
def aacircle(surface, color, pos, radius,  start_angle=0, end_angle=2*math.pi):
    # draw outline
    out_pts = aacircle_pts(pos, radius, start_angle, end_angle)
    pygame.draw.aalines(surface, color, False, out_pts)
    
    
    
    
def aabezier(surface, color, pts, fill=False, aa=True):    
    # draw a bezier curve
    real_pts = [pts]            
    pts =[]
    for pt_seq in real_pts:
        pts = pts + bezier_curve.render_bezier(pt_seq)
            
        
    if fill:
        pygame.draw.polygon(surface, color, pts)
    else:
        if aa:
            pygame.draw.aalines(surface, color, False, pts)
        else:
            pygame.draw.lines(surface, color, False, pts)
            
            
            
        
if __name__=="__main__":
   import skeleton
   
   def draw(surface):
     surface.fill((0,0,0))
     aabezier(surface, (255,128,0), [(50,50), (100, 100), (300, 100), (300, 300), (400,400), (100,200), (100,100)])
   
   
   s = skeleton.Skeleton(draw_fn = draw)
   s.main_loop()
   