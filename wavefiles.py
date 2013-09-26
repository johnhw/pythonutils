import wave, numpy

def read_wave(file):
    """
    Read an audio file in .WAV format and return it as a numpy array with values -1.0 -- 1.0.    
    
    @type file: string
    @param file: name of the .WAV file to read
    @rtype: numpy array, number, number, number
    @return: array of signal values. 1 column for mono signals, 2 columns for stereo. Followed by number of channels, sampling frequency and width of original data in bytes (1==8 bits, 2==16 bits)
    
    """
    wave_read = wave.open(file)
    frames = wave_read.getnframes()            
    data = wave_read.readframes(frames)
    
    channels = wave_read.getnchannels()
    freq = wave_read.getframerate()
    width = wave_read.getsampwidth()
    
    if width==1:
        datan = numpy.fromstring(data, dtype=numpy.int8)
    else:
        datan = numpy.fromstring(data, dtype=numpy.int16)
        
    datan = datan.reshape(len(datan)/channels, channels)        
    
    scale = 2 ** (8*width-1)
    return (datan.astype(numpy.float64)/scale, channels, freq, width)
    
    
def save_wave(name, data, channels=1, freq=44100, width=2):
    """
    Write a numpy array to .WAV format. Data should be in range -1.0 -- 1.0.
    
    @type name: string
    @param name: Name of file to save to
    @type data: numpy array
    @param data: Data to write. Range -1.0 to 1.0. 1 column for mono, 2 column for stereo.
    @type channels: number
    @param channels: Number of channels of audio
    @type freq: number
    @param freq: sampling frequency to set the wave file to. Should be 11025, 22050, 44100, 48000, etc.
    @type width: number
    @param width: width of data to write out in bytes. 1==write in 8 bit, 2==write in 16 bit.
    @rtype: None
    """

    nframes = len(data)
    w = wave.open(name, "wb")
    w.setparams((channels, width, freq, nframes, 'NONE', 'no compression'))
    
    scale = 2 ** (8*width-1)
    d = data.ravel()*scale
    if width==2:
        w.writeframes(d.astype(numpy.int16).tostring())
    else:
        w.writeframes(d.astype(numpy.int8).tostring())
            
    w.close()
    
   