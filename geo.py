from math import *
from geometry import to_radians, to_degrees

# return difference in meters between p1 and p2 in lat, long form
def latlondistance(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    dlat = to_radians(lat2-lat1)
    dlon = to_radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))    
    return c*6371000

def latloncourse(p1, p2):
    lat1, lon1 = to_radians(p1[0]), to_radians(p1[1])
    lat2, lon2 = to_radians(p2[0]), to_radians(p2[1])
    
    if cos(lat1)<1e-10:
        if lat>0:
            return pi
        else:
            return -pi
        
    tc1=atan2(sin(lon1-lon2)*cos(lat2),
           cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon1-lon2))
    return tc1
    
    
if __name__=="__main__":
    a = (55.874465, -4.292040)
    b = (55.874503, -6.292026)
    print to_degrees(latloncourse(a,b))
    print latlondistance(a,b)
    print to_degrees(-0.730643)
    print to_degrees(17.719831%(pi*2))