import numpy, pickle, os


class CalibrationData:
    """Calibration data for a SHAKE. Assumes linear calibration of the form v = Ax+B"""
    def __init__(self):            
        self.acc_a = numpy.eye(3,3)
        self.acc_b = numpy.zeros(3,)
        self.mag_a = numpy.eye(3,3)
        self.mag_b = numpy.zeros(3,)
        self.gyro_a = numpy.eye(3,3)
        self.gyro_b = numpy.zeros(3,)
        
        
def read_calibration_data(serial):
    """Read calibration data from a file for one SHAKE"""
    fname = serial+'_full_calibration.dat'
    if os.path.exists(fname):
        infile = open(fname, 'rb')
        if infile:
            try:
                calib = pickle.load(infile)                
                infile.close()                
                return calib
            except:
                infile.close()
                return CalibrationData()
                
    # create a new one if none loaded
    return CalibrationData()
            
def write_calibration_data(serial, calib):
    """Write calibration data from a file for one SHAKE"""
    fname = serial+'_full_calibration.dat'
    outfile = open(fname, 'wb')
    pickle.dump(calib, outfile)
    outfile.close()
    