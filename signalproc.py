import numpy

def downsample(x, p):
    m = numpy.reshape(x, (len(x)/(p), (p)))
    return numpy.sum(m, axis=1)