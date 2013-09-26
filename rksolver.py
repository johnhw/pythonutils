import numpy, math
  
  
def iszeros(a):
    allzero = True
    for v in a:
        if v!=0.0:
            allzero = False
    return allzero
  
  

  
def ray_triangle(self, ray, triangle):
     u = triangle[0] - triangle[1]
     v = triangle[1] - triangle[2]
     n = numpy.cross(u,v)
     
     nnorm = n / numpy.sqrt(numpy.sum(numpy.sqr(n)))
     
     if iszeros(n):
        return (False, None, None)
        
     direction = ray[1] - ray[0]
     w0 = ray[0] - triangle[0]
     a = -numpy.dot(n, w0)
     b = numpy.dot(n, direction)
     if abs(b)<1e-6:
        if a==0:
            return (True, None, None)
        else:
            return (False, None, None)
    r = a/b
    if r<0.0:
        return (False, None, None)
    if r>1.0:
        return (False, None, None)
        
    i = ray[0]+r*direction
    uu = numpy.dot(u,u)
    uv = numpy.dot(u,v)
    vv = numpy.dot(v,v)
    w = i - triangle[0]
    wu = numpy.dot(w,u)
    wv = numpy.dot(w,v)
    D = uv*uv - uu*vv
    s = (uv * wv - vv*wu)/D
    if s<0.0 or s>1.0:
        return (False, None, None)
        
    t = (uv*wu-uu*wv)/D
    if t<0.0 or t>1.0:
        return (False, None, None)
        
    reflected = direction - 2*(numpy.dot(n,direction) * n)
    return (True, i, reflected)
    
     

     
     
def matrix_transform(matrix, y):
    v = numpy.dot(matrix, numpy.hstack((y, [1])))
    l = math.sqrt(numpy.sum(v*v))
    return (v[0:3],l)

def distance(a,b):
    return math.sqrt(numpy.sum((a-b)*(a-b)))
    
def create_identity():
    return numpy.eye(4)

def translate(matrix, v):
    v = [[0,0,0,v[0]],[0,0,0,v[1]],[0,0,0,v[2]],[0,0,0,1]]
    return numpy.dot(matrix,v)
    
def scale(matrix, v):
    v = [[v[0],0,0,0],[0,v[1],0,0],[0,0,v[2],0],[0,0,0,1]]
    return numpy.dot(matrix, v)
    
def rotate(matrix, angle, axis):
    c = math.cos(angle)
    s = math.sin(angle)
    C = 1-c
    as = axis*s
    aC = axis*C        
    xyC = axis[0]*axis[1]*C
    yzC = axis[1]*axis[2]*C
    zxC = axis[2]*axis[0]*C
    v = [[axis[0]*aC[0], xyC-as[2], zxC+as[1],0],
         [xyC+as[2], axis[1]*aC[1]+c, yzC-as[0], 0],
         [zxC-as[1], yzC+as[0], z*aC[2]+c, 0],
         [0,0,0,1]]
    return numpy.dot(matrix, v)
     
    
    


    

   
    
class Spring:
    def __init__(self, to, k, length, damping, breaking):
        self.to = to       
        self.k = k
        self.length = length
        self.damping = damping
        self.breaking = breaking
        self.broken = False
        
    def evaluate(self, y1):        
        vel = y1[3:6]        
        y2 = self.to.get_y()
        d = y1[0:3] - y2[0:3]
        l = math.sqrt(numpy.sum(d*d))
        direction = d/l
        dlen  = l-self.length
        
        if abs(dlen)>self.breaking:
            self.k = 0
            self.broken = True
            self.damping = 0
            
        return dlen*-direction*self.k-self.damping*vel
        
                
class Collision:
    def __init__(self):
        pass
        
    def collision_possible(self, y):
        return False
        
    def collision_apply(self, y):
        return y


        
class TriangleCollision:
    def __init__(self, tri):
        self.tri = tri
        
    def collision_possible(self, y):
        # velocity vector
        ray = (y[0:3], y[0:3]+y[3:6])
        (hit, point, reflected) = ray_triangle(ray, self. tri)
        return hit and reflected
        
    def collision_apply(self, y):
        (hit, point, reflected) = ray_triangle(ray, self. tri)
        if hit and reflected:
            y[3:6] = reflected
        return y
        
    
            
            
            
            
    
        
class Field:
    def __init__(self):
        pass
        
        
    def evaluate(self, y):
        return numpy.array([0,0,0])
        
        
    def matrix(self, matrix):
        self.matrix = numpy.dot(self.matrix, matrix)
        
    def rotate(self, matrix, axis, angle):
        matrix = rotate(self.matrix, axis, angle)
        
    def translate(self, pos):
        matrix = translate(self.matrix, pos)
        
    def scale(self, scl):
        scale = translate(self.matrix, scl)
        
        
class ConstantField(Field):
    def __init__(self, force):
        self.force = force        
        
        
    def evaluate(self, y):
        return self.force
        
        
class Attractor(Field):
    def __init__(self, matrix, exponent):        
        self.matrix = matrix
        self.exponent = exponent
 
        
    def evaluate(self, y):
        (d,l) = matrix_transform(self.matrix, y[0:3])        
        direction = d/l
        return math.pow(l,exponent) * direction
                    
        
       


       
# class SolidBox(Field):
    # def __init__(self, matrix, force):
        # self.matrix = matrix
        # self.force = force

        
    # def evaluate(self, y):
        # (d,l) = matrix_transform(self.matrix, y[0:3])        
        # direction = d/l
        
        # inside = True
        # if not (d[0]>-0.5 and d[0]<0.5):
            # inside = False
        # if not (d[1]>-0.5 and d[1]<0.5):
            # inside = False
        # if not(d[2]>-0.5 and d[2]<0.5):
            # inside = False
            
        # if inside:
            # return self.force*direction
        # else:
            # return 0*direction
            
        

        
class ReflectEllipsoid(Field):
    def __init__(self, matrix, force):
        self.matrix = matrix
        self.force = force

        
    def evaluate(self, y):
        (d,l) = matrix_transform(matrix, y[0:3])
        
        direction = d/l
        
        
        if l<1:
            return force*-direction
        else:
            return 0*-direction
            
            
        
class BoundedBoxField(Field):
    def __init__(self, matrix, field):
        self.matrix = matrix
        self.field = field

        
    def evaluate(self, y):
        (d,l) = matrix_transform(self.matrix, y[0:3])                
        
        
        inside = False
        if d[0]>-0.5 and d[0]<0.5:
            inside = True
        if d[1]>-0.5 and d[1]<0.5:
            inside = True
        if d[2]>-0.5 and d[2]<0.5:
            inside = True
            
        if inside:
            return self.field.evaluate(y)
        else:
            return 0*d
            
            
class BoundedEllipsoidField(Field):
    def __init__(self, matrix, field):
        self.matrix = matrix
        self.field = field

        
    def evaluate(self, y):
        (d,l) = matrix_transform(self.matrix, y[0:3])        
        direction = d/l
        
        
        if l<1:
            return self.field.evaluate(f)
        else:
            return 0*d
        
        
        
class Turbulence(Field):

    def __init__(self, level, correlation):

        self.level = level
  
        self.correlation = correlation
        self.noise = numpy.zeros((3,))
        
    
    def evaluate(self, y):
        self.noise = (1.0-self.correlation) * self.noise + self.correlation * numpy.random.standard_normal((3,))
        return self.noise *self.level
        
        
        
    

class Friction(Field):
    def __init__(self, f1, f2, matrix):
        #nb matrix specifies crossover (always happens at v=1.0 after transform)
        self.f1 = f2
        self.f2 = f2
        self.matrix = matrix
        
    def evaluate(self, y):
        (v,l) = matrix_transform(self.matrix, y[3:6])
        
        direction = v/l
        if l<1.0:
            return self.f1 * -direction
        else:
            return self.f2 * -direction
        
        
    
class Mass:

    def __init__(self, mass, damping):
        self.y = numpy.array([0,0,0,0,0,0])
        self.fields = []
        self.springs = []
        self.mass = mass
        self.damping = damping
        self.collisions = []
        
        
        
    def add_collision(self, collision):
        self.collisions.append(collision)
    
        
    def set_position(self, pos):
        self.y[0:3] = pos
        
    def set_velocity(self, vel):
        self.y[5:6] = vel
    
    def add_spring(self, other_mass, k, length, damping, breaking):
        spring = Spring(other_mass, k, length, damping, breaking)
        self.springs.append(spring)
        
        
    def add_field(self, field):
        self.fields.append(field)

        
    def compute_collisions(self):
        for collision in self.collisions:
            if collision.collision_possible(self.y):
                self.y = collision.apply_collision(self.y)

    def update(self, dt):
        self.rksolve(dt)
        self.y[3:6] = self.y[3:6] * self.damping
        self.compute_collisions()
        
        
    def get_y(self):
        return self.y
        
    def compute_forces(self):
        f = numpy.zeros((3,))
        
        for field in self.fields:
            f = f + field.evaluate(self.y)
            
        for spring in self.springs:
            f = f + spring.evaluate(self.y)
            
        return f
    
    def integrator(self,y):
        f = self.compute_forces()
        yd = numpy.zeros((len(y),))
        yd[0:3] = y[3:6] 
        yd[3:6] = f[0:3]/self.mass        
        return yd
                
    
    def rksolve(self, dt):
        k1 = self.integrator(self.y)
        k2 = self.integrator(self.y+dt/2*k1)
        k3 = self.integrator(self.y+dt/2*k2)
        k4 = self.integrator(self.y+dt*k3)
        self.y = self.y + dt/6.0*(k1+2*k2+2*k3+k4)

