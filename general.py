import time, math

# return a sensible string interpretation of the given seconds
def format_time(seconds):    
    
    if seconds<60:
        return "%d seconds" % seconds
    if seconds>60 and seconds<3600:
        return "%d minutes %d seconds" % (seconds//60, seconds%60)  
    if seconds>=3600:
        return "%d hours %d minutes %d seconds" % (seconds//3600, (seconds//60)%60, seconds%60)


# return a value from 0--1 suitable for damping
def damping_value(x):   
    return 1-1.0/math.exp(x)
        

# return the time since tick was last called. Always returns 0 for first call
class DeltaT:
    def __init__(self):
        self.last_time = None
        
    def tick(self):
        t = time.clock()
        if self.last_time!=None:
            dt = t - self.last_time
        else:
            dt = 0.0
            
        self.last_time = t
        return dt
        
        
        
# Schedules events at some time in the future.
# add events with a given delay
# then call tick every loop with the time since the last call to tick
class Scheduler:
    def __init__(self):
        self.queue = []
        
    # if events are recurring, they should return True until they want to be stopped
    def add_event(self, t, callback, recurring = False):
        self.queue.append((t, callback, recurring, t))
        
        
    def tick(self, dt):
        kill_list = []
        
        # decrement all waiting
        for i in range(len(self.queue)):                
            t, call, recurring, orig_t = self.queue[i]
            t = t - dt
            self.queue[i] = (t, call, recurring, orig_t)
            
            
            if t<0.0:   
                keep_running = call()
                
                # either kill or reinstate 
                if not recurring or not keep_running:            
                    kill_list.append(self.queue[i])
                else:
                    self.queue[i] = (orig_t, call, recurring, orig_t)
            
        # remove expired
        for kill in kill_list:
            self.queue.remove(kill)     
            
            
            
            
if __name__=="__main__":
    start_time = time.clock()
    
    def hello():
        print "Hello!"
        
    def tick():
        print "Tick..."
        return time.clock()-start_time<4.0
        
        
        
    d = DeltaT()
    s = Scheduler()
    s.add_event(3, hello)
    s.add_event(0.25, tick, recurring = True)
    
    for i in range(100):
        time.sleep(0.1)
        dt = d.tick()
        s.tick(dt)