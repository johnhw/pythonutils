

# connect to a shake, storing the default setting
# n is the number of the shake in your program (i.e. if you connect to two shakes, use n=0 and n=1)
def get_shake_com(n = 0):

    # try and read default
    fname = "shake_default_%d.no" % n    
    com = None
    try:
        f = open(fname, 'r')
        
        com = f.readline().strip()
        f.close()
    except:
        pass
        
        
    # prompt for com port
    if com!=None:
        response = raw_input("Connect to SHAKE on COM (ENTER=%s, or r to RFCOMM connect):" % com).strip()
    else:        
        response = raw_input("Connect to SHAKE on COM (or r to RFCOMM connect):").strip()
        
    # hardwired for a particular shake
    if len(response)!=0:            
        if response=='r':
            com = '00:04:3e:23:47:3a'
        else:
            com = int(response)
            
                
    # store default        
    try:
        f = open(fname, 'w')
        
        f.write("%s\n" % com)
        f.close()
    except:
        pass
        
    return com
        
    
    

