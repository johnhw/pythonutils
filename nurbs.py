import math, time
from vector import *


class Nurbs:
    def __init__(self, pts, knots, order=3):
        self.pts = pts
        self.knots = vscale(knots, 1.0/max(knots))
        self.order = order
        
        
        
    # compute blending function
    def N(self, i, k, u):       
                    
        t = self.knots        
        
        
        if k==0:
            if u>=t[i] and u<=t[i+1]:
                return 1.0
            else:
                return 0.0
            
        if t[i+k]-t[i]!=0:
            a = (u - t[i]) / (t[i+k]-t[i])
        else:
            a = 0.0
            
        if t[i+k] - t[i]!=0:
            b = (t[i+k]-u) / (t[i+k] - t[i])
        else:
            b = 0.0
            
        v = a*self.N(i,k-1,u) + b*self.N(i+1,k-1,u)
        return v
        
        
    
    def evaluate(self,  u):
    
        eps = 1e-10
        
        if u<min(self.knots)+eps:
            u = min(self.knots)+eps
            
        if u>=max(self.knots)-eps:
            u=max(self.knots)-eps
            
        # scale
        weighted_pts = [vscale(pt[0:-1],pt[-1])+[pt[-1]] for pt in self.pts]
        
                
        pts = []
        for i in range(len(self.pts)):
            pts.append(vscale(weighted_pts[i], self.N(i, self.order, u)))
            
        eval_pt = reduce(vadd, pts)
        
        
        # unscale
        if eval_pt[-1]!=0:
            unweighted_pt = vscale(eval_pt[0:-1], 1.0/eval_pt[-1]) 
        else:
            unweighted_pt = eval_pt[0:-1]
            
        
        return unweighted_pt
        
        

if __name__=="__main__":
    import skeleton, pygame
    
    
    # two2 = 0.5
    # n= Nurbs([(200,100,1.0), 
    # (200,200,two2),
    # (100,200,1.0),
    # (0,200,two2),
    # (0,100,1.0),
    # (0,0,two2),
    # (100,0,1.0),
    # (200,0,two2),
    # (200,100,1.0)], knots=[0,0,0,0.5,0.5,1,1,3.0/2.0,3.0/2.0,2,2,2])
    
    n = Nurbs([(50,50,1),(100,200,1),(200,200,1), (400,400,1)], knots=[0,0,1,2,3,4,4,4])
    
  
    
    def draw(surface):
        pts = []
        for i in range(500):
            pts.append(n.evaluate(i/100.0))
            
        for pt in n.pts:
            pygame.draw.circle(surface, (0,0,0),pt[:-1],5)
            
        pygame.draw.aalines(surface, (0,0,0), False, pts)
        
    
    s = skeleton.Skeleton(draw_fn = draw)
    s.main_loop()
    