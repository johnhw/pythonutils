import sys, time, os, math
import numpy
import scipy.signal
import pickle
from shake import *                                                                                
from filter import Filter, Interpolator
from calibration import *


        

# convert a rotation matrix to three euler angles        
def rotation_to_euler(m, parity=False):

    if parity:
        i = 2
        j = 0
        k = 1
    else:
        i = 2
        j = 1
        k = 0
    
    cy = math.sqrt(m[i,i]*m[i,i] + m[j,i]*m[j,i])
    if cy > 1e-6:
        az = -math.atan2(m[k,j],m[k,k])
        ay = -math.atan2(-m[k,i],cy)
        ax = -math.atan2(m[j,i],m[i,i])
    else:
        az = -math.atan2(-m[j,k],m[j,j])
        ay = -math.atan2(-m[k,i],  cy)
        ax = 0.0
        
        
    if parity: 
        ax, ay, az = -ax, -ay, -az
    return ax, ay, az
    
        
# convert euler to rotation matrix 'rxyz' order
def euler_to_rotation(ai, aj, ak):
    i = 2
    j = 1
    k = 0

    ai, ak = ak, ai
    ai, aj, ak = -ai, -aj, -ak

    si, sj, sh = math.sin(ai), math.sin(aj), math.sin(ak)
    ci, cj, ch = math.cos(ai), math.cos(aj), math.cos(ak)
    cc, cs = ci*ch, ci*sh
    sc, ss = si*ch, si*sh

    M = numpy.identity(3, dtype=numpy.float64)        
    M[i,i] =  cj*ch;  M[i,j] =  sj*sc-cs; M[i,k] =  sj*cc+ss
    M[j,i] =  cj*sh;  M[j,j] =  sj*ss+cc; M[j,k] =  sj*cs-sc
    M[k,i] = -sj;     M[k,j] =  cj*si;    M[k,k] =  cj*ci
    
    return M
       
    
# compute the rotation matrix given magnetometer and accelerometer readings        
def to_rotation_matrix(acc, mag):
    
    # normalize vectors to the sphere
    a = numpy.array(acc)
    b = numpy.array(mag)
    r1 = math.sqrt(numpy.sum(a*a))
    r2 = math.sqrt(numpy.sum(b*b))
    a = a / r1
    b = b / r2
    
    # compute centre point of line to centre of sphere
    av = (a+b)
    rav = math.sqrt(numpy.sum(av*av))
    av = av / rav
    
    # compute line between acc and mag
    dif = (a-b)
    rdif = math.sqrt(numpy.sum(dif*dif))
    dif = dif / rdif
    
    # use these as forward and right vectors; compute the up from these
    # NB a and dif aren't exactly perpindicular -- if you need perpindicularity, use av and dif
    forward = a
    right = -dif
    up = -numpy.cross(forward, right)
    right = numpy.cross(forward, up)
    
    rotation = numpy.transpose(numpy.vstack((up, right, forward)))        
    return rotation

# convert an axis/angle pair to a rotation matrix    
def axis_angle_to_matrix(axis, angle):
        alen = math.sqrt(axis[0]*axis[0]+axis[1]*axis[1]+axis[2]*axis[2])
        x = axis[0] / alen
        y = axis[1] / alen
        z = axis[2] / alen
        c = math.cos(angle)
        s = math.sin(angle)
        xs = x*s
        ys = y*s
        zs = z*s
        xc = x*c
        yc = y*c
        zc = z*c
        xyc = x*yc
        yzc = y*zc
        zxc = z*xc
        rot = numpy.array([[x*xc+c, xyc-zs, zxc+ys], [xyc+zs,y*yc+c, yzc-xs], [zxc-ys, yzc+xs, z*zc+c]])
        return rot
        
    # convert a sphere point to a rotation
def sphere_to_rotation(rotmatrix, orig):
    (xa,ya,za) = numpy.dot(rotmatrix, orig.copy())      
    vec = numpy.array([xa, ya, za], dtype=numpy.float64)
    point =  orig.copy()
    vec = vec / math.sqrt(vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2])
    ang = math.acos(numpy.dot(vec, point))
    axis = numpy.cross(vec, point)                
    r = axis_angle_to_matrix(axis,ang)
    return r
    
    
def compute_twist(self, rotmatrix, axis):       
  
  if axis==0:
    arr1 = numpy.array([1.0,0.0,0.0])
    arr2 = numpy.array([1.0,0.0,1.0])
  elif axis==1:
    arr1 = numpy.array([0.0,1.0,0.0])
    arr2 = numpy.array([0.0,0.0,1.0])
  elif axis==2:
    arr1 = numpy.array([0.0,0.0,1.0])
    arr2 = numpy.array([0.0,1.0,0.0])
    
  r = self.sphere_to_rotation(rotmatrix, arr1)
  m = numpy.dot(r,rotmatrix)     
  (x3,y3,z3) = numpy.dot(m, arr2)           
  
  if axis==0:
    ang = -math.atan2(y3,z3)
  elif axis==1:
    ang = -math.atan2(x3,z3)
  elif axis==2:
    ang = -math.atan2(x3,y3)
  return ang
           
class ShakeInterface:

    def print_stat(self, s, com):
            #print out some stats
           
            print "---==SHAKE details==---" 
            print "  => SHAKE No. [%s] on COM port %d" % (s.info_serial_number(),com)
            
            print "        HW revision %s" % (str(s.info_hardware_revision())[:4])
            print "        Firmware version %s" % (str(s.info_firmware_revision())[:4])                                   
            print "        at %d deg. C" % (s.read_temperature())
            power = s.read_power_status()[1]
            if power & SHAKE_EXT_POWER != 0:
                pwr_stat = "        On external power"
            else:
                pwr_stat = "        Battery at %d percent " % ((float(s.read_battery_level()[1]) / SHAKE_BATTERY_MAX)*100.0)
                
            if power & SHAKE_BAT_CHARGING !=0:
                pwr_stat = pwr_stat + " [charging]"
            if power & SHAKE_BAT_FULL !=0:
                pwr_stat = pwr_stat + " [CHARGED]"
            print pwr_stat
            print
            print "   => Settings"
            

            p = s.read_power_state()[1]
            for sensor in ((SHAKE_POWER_ACC, "Accelerometer"), (SHAKE_POWER_GYRO, "Gyroscope"), (SHAKE_POWER_VIB, "Vibrator"), (SHAKE_POWER_MAG, "Magnetometer"), (SHAKE_POWER_TEMP, "Temperature"), (SHAKE_POWER_ANALOG, "Analog"), (SHAKE_POWER_NAV, "Navigation switch")):
                
                if p & sensor[0]:
                    print "        %s  *ON*" % sensor[1]
                else:
                    print "        %s -off- " % sensor[1]
                
            
            print "         => Sample rates"
            for sensor in ((SHAKE_SENSOR_ACC, "Accelerometer"), (SHAKE_SENSOR_GYRO, "Gyroscope"), (SHAKE_SENSOR_MAG, "Magnetometer"), (SHAKE_SENSOR_HEADING, "Heading"), (SHAKE_SENSOR_CAP0, "Capacitive 0"), 
            (SHAKE_SENSOR_CAP1, "Capacitive 1"), (SHAKE_SENSOR_ANA0, "Analog 0"),  (SHAKE_SENSOR_ANA1, "Analog 1"),):
                filter = s.read_digital_filter(sensor[0])[1]
                
                if filter & 1 == 1:
                    fil = "Filtered"
                    if filter & 2 == 2:
                        fil = fil + " with min. phase filter"
                    else:
                        fil= fil + " with linear phase filter"                
                else:
                    fil = "Unfiltered"
                    
                print "            %s : sample rate %dHz [%s]" % (sensor[1], s.read_sample_rate(sensor[0])[1], fil)    
                
            if s.read_data_format()[1] & 2 == 2:
                data_format = "Raw (binary) mode"
            else:
                    data_format = "ASCII mode"
                
            if s.read_data_format()[1] & 4 == 4:
                data_format = data_format + " [timestamps enabled]"
            
            print "         Data format %s" % (data_format)
            
            acc_mode = s.read_acc_config()[1]
            if acc_mode&1==0:
                print "         Accelerometer range +/- 2g",
            else:
                print "         Accelerometer range +/- 6g",
            
            if acc_mode&2==0:
                print "no highpass"
            else:
                print "highpass enabled"
            
            if s.read_calib_bypass()[1]!=0:
                print "         Calibration bypassed"
            else:
                print "         Calibration enabled"
                
            if s.read_cx_bypass()[1]!=0:            
                print "         Cross-axis bypassed"
            else:
                print "         Cross-axis calibration enabled"
                
            if s.read_packet_streaming()[1]==0:
                print "         Packet streaming mode"
            else:
                print "         Request mode"
     
            
                       
            print 
            print
        

    # adjust filters to suit (filters are given in Hz)
    def __init__(self, coms=(4,5), rate=100, nav_callback=None, acc_filter=2, gyro_filter=25, mag_filter=2, use_interpolation=True):
        """Specify the com ports for each shake (specify as many as you want), and the
        sampling rate in Hz"""
        
        self.shakes = []
        self.old_states = []
        self.calibrations = []
        self.orientators = []
        
        
        
        # create filter coefficients
        nyquist = float(rate)/2.0
        
        # NB change me for phone
        acc_filter_ba = scipy.signal.butter(2, acc_filter/nyquist, btype='low')        
        gyro_filter_ba = scipy.signal.butter(2,  gyro_filter/nyquist, btype='low')        
        mag_filter_ba = scipy.signal.butter(2, mag_filter/nyquist, btype='low')
                     
        self.filters = []
        self.interpolators = []
        self.use_interpolation = use_interpolation
                
        for com in coms:        
        
            # generate the filters
            filters = []
            for i in range(3):
                filters.append(Filter(acc_filter_ba[0],acc_filter_ba[1]))
            for i in range(3):
                filters.append(Filter(gyro_filter_ba[0],gyro_filter_ba[1]))
            for i in range(3):
                filters.append(Filter(mag_filter_ba[0],mag_filter_ba[1]))
            
            
            # add the interpolators and filters
            interpolators = []
            for i in range(9):
                interpolators.append(Interpolator(wrap_limit=100))
            
            self.filters.append(filters)
            self.interpolators.append(interpolators)
            self.old_states.append(numpy.zeros((9,)))
    
            
            # connect and set the values
            s = shake_device()
            s.connect(com)
            
            #enable packet streaming
            s.write_packet_streaming(0)        
            
            #set the sample rates
            s.write_sample_rate(SHAKE_SENSOR_ACC, rate)
            s.write_sample_rate(SHAKE_SENSOR_GYRO, rate)
            s.write_sample_rate(SHAKE_SENSOR_MAG, rate)
            
            # enable min_phase filter
            s.write_digital_filter(SHAKE_SENSOR_ACC, 1)
            s.write_digital_filter(SHAKE_SENSOR_GYRO, 1)
            s.write_digital_filter(SHAKE_SENSOR_MAG, 1)
            
            #make sure calibration is on
            s.write_calib_bypass(0)
            s.write_cx_bypass(0)
            
            s.write_data_format(6) #binary with timestamps   
            s.write_acc_config(0) # make sure accelerometer is in default configuration
            
            # power all the sensor we need                        
            s.write_power_state(SHAKE_POWER_ACC | SHAKE_POWER_VIB | SHAKE_POWER_GYRO | SHAKE_POWER_MAG | SHAKE_POWER_NAV)
            
            # register the nav callback
            if nav_callback:
                s.register_event_callback(nav_callback)
                
            # print out the state of the device
            self.print_stat(s, com)
            
            #read in any previous calibration data
            self.calibrations.append(read_calibration_data(s.info_serial_number()))
            self.orientators.append(OrientationEstimator())
            
            
            self.shakes.append(s)
                               
                               

    def get_filtered_last_packet(self, interpolator, filter, state, old_state, time, use_filter=True):
        """Put the given value and timestamp through the interpolator; feed the results to
        the filter and return the most recent value"""
        interpolator.add_packet(state, time)        
        
        values = interpolator.get_packets()
        
        #return the last state if there are no new packets
        if len(values)<1:
            return old_state
        filtered = []        
        
        # feed packets to the filter
        for v in values:
            filtered.append(filter.filter(v))
                    
        # return the last packet
        if use_filter:
            return filtered[-1]
        else:
            return values[-1]
            
  
            
    def set_gyro_free(self, free):
        """Set gyro free spin mode"""
        for orientator in self.orientators:
            orientator.set_gyro_free(free)
        
    def close(self):
        self.write_calibration()
        for shake in self.shakes:
            shake.close()
            
    def write_calibration(self):    
        """Write out calibration for all SHAKEs connected"""
        i = 0
        for shake in self.shakes:
            write_calibration_data(shake.info_serial_number(), self.calibrations[i])
            i = i + 1
                
    def compute_rotation_matrices(self, use_filter = True, use_gyro=True):
        """Return the orientation matrices for all of the SHAKEs. Return value is (matrix, (adev, mdev)) where
        adev and mdev are the deviations of the magnetic and gravitational fields (1.0=no deviation)"""
        i = 0
        states = self.update_state(use_filter=use_filter, use_calibration=True)
        matrices = []
        deviations = []
        for state in states:
            orientator = self.orientators[i]
            # get the matrix
            (matrix, a_dev, m_dev, calibrating) = orientator.compute_orientation_matrix(state, use_gyro=use_gyro)
            matrices.append(matrix)
            deviations.append((a_dev, m_dev))
            i = i + 1                
        return (matrices, deviations)
        
    
    
    def get_euler_angles(self, use_gyro=False, use_filter=True):
        mats, devs = self.compute_rotation_matrices(use_gyro=use_gyro, use_filter=use_filter)
        
        eulers = []
        for mat in mats:
            euler = rotation_to_euler(numpy.linalg.inv(mat))
            eulers.append(euler)
            
        return eulers
    
    def update_state(self, use_filter=True, use_calibration=True):
        """Return the state of the sensors as a list of vectors (one vector for each shake). Uses filtering and interpolation"""
        states = []
        i  = 0
        for shake in self.shakes:
            
            calib = self.calibrations[i]
            interpolator = self.interpolators[i]
            filter = self.filters[i]
            old_state = self.old_states[i]
           
                        
            #gyro and accelerometer
            if use_calibration:
                acc = numpy.dot(calib.acc_a, numpy.array(shake.acc())) + calib.acc_b
                gyro = numpy.dot(calib.gyro_a, numpy.array(shake.gyro())) + calib.gyro_b            
                mag = numpy.dot(calib.mag_a, numpy.array(shake.mag())) + calib.mag_b            
            else:
                acc = numpy.array(shake.acc())
                gyro = numpy.array(shake.gyro())
                mag = numpy.array(shake.mag())                
                                                    
            state = numpy.hstack((acc, gyro, mag))
            
            # get the filtered samples (or the last sample, if no new stuff has arrived)
            tacc = shake.data_timestamp(SHAKE_SENSOR_ACC)
            
            if self.use_interpolation:
                for j in range(9):                
                    state[j] = self.get_filtered_last_packet(interpolator[j], filter[j],  state[j], old_state[j], tacc, use_filter)
            
                                                                                  
            states.append(state)
            i = i + 1
        self.old_states = states
        
        return states
        

    
        
        
# Skeleton class                                          
class OrientationEstimator:
        
        
    def get_heading(self, accx, accy, accz, magx, magy, magz):
        (inv, mdev, adev, calib) = self.compute_orientation_matrix(numpy.array([accx,accy,accz,0,0,0,magx,magy,magz]), use_gyro=False)
        inv = numpy.linalg.inv(inv)
        euler = rotation_to_euler(matrix, parity=True)
        return euler[2]
        
        
        
    def __init__(self):                                            
        """Create a new orientation estimator"""
        self.gyr1 = numpy.array([0.0,0.0,0.0])
        self.gyr2 = numpy.array([0.0,0.0,0.0])        
        self.last_time = time.clock()        
        
        self.free = False
        self.gyro_offset = None                        
        self.avg_state = None
        self.avg_energy = 0 

         
        self.avg_time = 0.85             # time to compute stationary. closer to 1.0 = longer time
        self.recalibrate_thresh = 400 # larger = tolerates more movement when determining stationary
        self.offset_rate = 0.7            # rate at which gyros track acc+mag when calibrating (closer to 1.0 is slower)
        self.gradual_rate = 0.95       # rate at which gyros track when not calibrating (closer to 1.0 is slower)

          
    # convert cartesian to spherical co-ordinates          
    def cart2sph(self, x, y, z):
        r = math.sqrt(x*x+y*y+z*z)
        phi = math.atan2(y, x)
        theta = math.acos(z/r)
        return (r,phi,theta)
        
        
    # compute the rotation to get from one sphere point to another as a quaternion
     #def compute_rotation(self,x1,y1,z1, x2,y2,z2):       
         #vec = numpy.array([x1,y1,z1], dtype=numpy.float64)
        # point = numpy.array([x2,y2,z2], dtype=numpy.float64)
        # ang = math.acos(numpy.dot(vec, point))
        # axis = numpy.cross(vec, point)
        # r = rotation_matrix_from_quaternion(quaternion_about_axis(ang, axis))
        # return r
           
        

    def set_gyro_free(self, free):
        """Set whether gyros are locked to accelerometer and magnetometer, or whether they are free. Note
        that in free mode, gyro readings will be used even if use_gyro is false"""
        self.free = free
    
    def compute_orientation_matrix(self, t, mag_field = 450, use_gyro=True):
          """Given a SHAKE state (after calibration/interpolation/filtering), compute the orientation of the device as a rotation matrix. Uses accelerometer and magnetometer and can also use gyroscopes for better response and stability"""
         
          #extract acc and mag
          acc = t[0:3]
          mag = t[6:9]
          
          # compute length of vectors and normalize
          r_acc = numpy.sqrt(numpy.sum(acc*acc))
          r_mag = numpy.sqrt(numpy.sum(mag*mag))
          acc = acc /  r_acc
          mag = mag /  r_mag
          
          
          #init the gyro offset
          if self.gyro_offset==None:
            self.gyro_offset = numpy.array([t[3], t[4], t[5]])
                
          # compute average state (approximate energy over last period)
          if self.avg_state == None:
            self.avg_state = t
            state_dist = 0
          else:
            self.avg_state = self.avg_time*self.avg_state + (1-self.avg_time) * t
            state_dist = numpy.sqrt(numpy.sum((self.avg_state - t) *(self.avg_state - t)))
            self.avg_energy = (self.avg_energy + state_dist) * self.avg_time
          
    
          
          
          if not self.free:
              # bring estimate and calibration towards 0 if stopped moving              
              if self.avg_energy < self.recalibrate_thresh:
                #bring in offsets and points
                self.gyro_offset = self.offset_rate * self.gyro_offset + (1-self.offset_rate) * t[3:6]
                self.gyr1= self.offset_rate * self.gyr1 + (1-self.offset_rate)*acc
                self.gyr2 = self.offset_rate * self.gyr2 + (1-self.offset_rate)*mag
                calibrating = True
              else:                
                # bring in points slowly when moving
                self.gyr1= self.gradual_rate * self.gyr1 + (1-self.gradual_rate)*acc
                self.gyr2 = self.gradual_rate * self.gyr2 + (1-self.gradual_rate)*mag
                calibrating = False
          else:
            calibrating = False
      
          #compute gyro rotation
          new_time = time.clock()
          dt = self.last_time - new_time
                  
          # convert from 10ths of degrees per second to radians per dt
          scale = (2*math.pi*dt)/3600.0
          
          # compute gyro rotation
          vecr = (t[3:6]-self.gyro_offset) * scale          
          grot = euler_to_rotation(vecr[1], vecr[0], vecr[2])                    
          self.last_time = new_time
      
          # update gyro points
          self.gyr1 = numpy.dot(grot, self.gyr1)
          self.gyr2 = numpy.dot(grot, self.gyr2)
        
                               
          # compute the rotation matrix
          if use_gyro or self.free:
            inv_rotate = numpy.transpose(to_rotation_matrix(self.gyr1[0:3], self.gyr2[0:3]))
          else:
             inv_rotate = numpy.transpose(to_rotation_matrix(acc, mag))
      
                                             
          acc_deviation = r_acc / 1000.0
          mag_deviation = r_mag / mag_field
                     
          return (inv_rotate, acc_deviation, mag_deviation, calibrating)


 