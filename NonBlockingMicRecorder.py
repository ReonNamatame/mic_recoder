#recording functionality
import pyaudio #handling recording function
import wave #handling .wav file
from os import makedirs, listdir

class VoiceRecorder(object):

    def __init__(self, wfile="record.wav", dst="./", overwrite=False):
        # dst must be ended with "/"
        if dst[-1] != "/":
            print("Destination must be ended with \"/\"")
            raise NotADirectoryError
        # check if dst already exists. If doesn't, make new dir
        makedirs(dst, exist_ok=True)
        # overwrite flag enables your record files not to be overwritten, if overwrite is False
        if overwrite == False and set.intersection(set(wfile), listdir(dst)) != set():
            print("Same wavfile exists in {0}\nYou were about to overwrite {1}\nIf you wouldn't mind it, set overwrite flag True".format(dst, dst+w))
            raise FileExistsError
        
        # recording time (unit: s)
        self.__record_time = 5
        # file name
        self.__output_wavfile = wfile
        # index number of microphone
        self.__idevice = 1
        # format of audio
        self.__format = pyaudio.paInt16
        # monaural
        self.__nchannels = 1
        # sampling rate,which is usually 16KHz In case of raspberryPi, you need 44.1kHz instread
        self.__sampling_rate = 44100 #8192*2
        # number of extracted data at a time,that is called chunk, mostly 1024 Byte at a time
        self.__chunk = 1024
        # get device information
        self.__audio = pyaudio.PyAudio()
        # instance of stream obj for making wav file
        #audio.open() method returns a new Stream instance taking some arguments for configuration
        self.__stream = self.__audio.open(
            format = self.__format,
            channels = self.__nchannels,
            rate = self.__sampling_rate,
            input = True,
            output = False,
            input_device_index = self.__idevice, # device1(Mouse_mic) will be used for input device
            frames_per_buffer = self.__chunk,
            stream_callback = self.callback
        )
        self.callback_on = True
        self.byte_data = bytearray()
        self.__stream.start_stream()
        
        self.prev = 0
        self.next = self.__chunk*2
    
    def setConfig(self, time_sec=3, outfile=["record.wav"], device_index=1, sampling_rate=44100, chunk=2**10, \
                   format=pyaudio.paInt16, nchannels=1):
        # configure foundimental information
        
        # recording time (unit: s)
        self.__record_time = time_sec
        # file name
        self.__output_wavfile = outfile
        # index number of microphone
        self.__idevice = device_index
        # sampling rate,which is usually 16kHz
        self.__sampling_rate = sampling_rate
        # number of extracted data at a time,that is called chunk
        self.__chunk = chunk
        # format of audio
        self.__format = format
        # monaural
        self.__nchannels = nchannels
        
    def callback(self, in_data, frame_count, time_info, status):
        #print(len(in_data), frame_count) #=> class "bytes", class "int"
        if self.callback_on == True:
            self.byte_data.extend(in_data)
            #print("byte_data = ", len(self.byte_data)/2048)
        # This app will not use output functionality, so returns tuple of none and paContinue
        return (None, pyaudio.paContinue)
    
    def showDeviceInfo(self):
        for i in range(self.__audio.get_device_count()):
            print(self.__audio.get_device_info_by_index(i))
    
    def getStream(self):
        return self.__stream
    
    def getByteData(self, begin, end):
        return self.byte_data[begin:end]
        
    def getChunk(self):
        return self.__chunk
    
    def getRecordTime(self):
        return self.__record_time

    def getAudioFileList(self):
        return self.__output_wavfile
    
    def makeWavFile(self, frames, wfile, mode='wb'):
        wavefile = wave.open(wfile, mode)
        wavefile.setnchannels(self.__nchannels)
        wavefile.setsampwidth(self.__audio.get_sample_size(self.__format))
        wavefile.setframerate(self.__sampling_rate)
        wavefile.writeframes(bytes(frames))
        wavefile.close()
        return wfile

    def closeAll(self):
        #stop and close audio stream
        self.__stream.stop_stream()
        self.__stream.close()
        self.__audio.terminate()
        #make wav file that is made of stream byte data
        self.makeWavFile(self.byte_data, self.__output_wavfile)
        print("pyaudio was terminated")

### end of VoiceRecorder

if __name__ == "__main__":
    import time

    _rec = VoiceRecorder(wfile="reco1.wav", dst="./", overwrite=False)
    
    print("recording")

    time.sleep(_rec.getRecordTime()) # wait N seconds till record finishes.

    print("finished")

    _rec.closeAll()