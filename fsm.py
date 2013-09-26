

class FSM:
    def __init__(self):
        self.states = []
        self.messages = []
        self.transitions = {}       
        self.transition_froms = {}
        self.state = None
        self.default = None
        self.always_reset =  False
        
    
    #set whether a missing transition means reset or stay where you are
    def set_always_reset(self, reset_mode):
        self.always_reset = reset_mode
        
        
    def set_start(self, state):
        self.default = state
        
    def add_transition(self, from_state, to_state, msg):
    
        # use first state given if no others
        if len(self.states)==0:
            self.default = from_state
            self.reset()
            
        self.transition_froms[from_state] = self.transition_froms.get(from_state, []).append(msg)
        
        self.transitions[(from_state, msg)] = to_state
        if from_state not in self.states: 
                self.states.append(from_state)
        if to_state not in self.states: 
            self.states.append(to_state)
        if msg not in self.messages:
            self.messages.append(msg)
            
            
    def __repr__(self):
        repr = ""
        for state in self.states:
            for msg in self.messages:
                key = (state,msg)
                if self.transitions.has_key(key):
                    repr = repr + "[%s -> (%s) -> %s]\n" % (state, msg, self.transitions[key])
        return repr
        
        
    def reset(self):
        self.state = self.default
        
        
    def get_transitions(self):
        return self.transition_froms[self.state]
        
        
    def transition(self, msg):
        key = (self.state, msg)
        if self.transitions.has_key(key):
            self.state = self.transitions(key)
        else:
            if self.always_reset:
                self.reset()
                
                
                
class ActionState:
    def __init__(self, name, enter_fn=None, exit_fn=None):
        self.enter_fn = enter_fn 
        self.exit_fn = exit_fn
        self.time = 0.0
        self.name = name
        
    def reset_time(self):
        self.time = 0.0
        
    def increment_time(self, dt):
        self.time += dt
    
        
    def __repr__(self):
        repr = name
        if self.enter_fn:
            repr = repr + " ->() "
        if self.exit_fn:
            repr = repr + " ()->"
                
        
        
def TimedTransition:
    def __init__(self, name, timeout=None):
        self.name = name
        self.timeout = timeout
        
    
        
class ActionTimedFSM:
    def __init__(self):
        self.fsm = FSM()
        
        
    def get_transitions(self):
        return self.fsm.transitions
        
    def add_transition(self, from_state, to_state, transition):
        self.fsm.add_transition(from_state, to_state, transition)
        
        
    def set_always_reset(self, mode):   
        self.fsm.set_always_reset(mode) 
        
        
    def transition(self, msg):
        key = (self.state, msg)
        if self.transitions.has_key(key):
            self.state = self.transitions(key)
        else:
            if self.always_reset:
                self.reset()
    
    def reset(self):
        self.fsm.reset()
        self.fsm.state.reset_time()
        
    def tick(self, dt):
        if self.fsm.state:
            self.fsm.state.increment_time(dt)
            transitions = self.fsm.get_transitions()
            min_time = 1e6
            min_transitions = None
            for t in transitions:
                if t.timeout<min_time:
                    min_time = t.timeout
                    min_transition = t
            if min_transitions and min_time>self.fsm.state.time:
                self.transition(min_transition)
            
            
            
        
        
        