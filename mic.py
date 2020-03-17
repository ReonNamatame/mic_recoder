import pyaudio #handling recording function
import wave #handling .wav file
from os import listdir, makedirs

#beginning of class Recorder
class Recorder:
#public methods
    def __init__(self):
        # recording time (unit: s)
        self.__record_time = 3
        # file name
        self.__output_wavfile = ["record.wav"]
        # index number of microphone
        self.__idevice = 1
        # format of audio
        self.__format = pyaudio.paInt16
        # monaural
        self.__nchannels = 1
        # sampling rate,which is usually 16KHz(=16kHz?) In the special case, raspberryPi needs 44.1kHz
        self.__sampling_rate = 44100 #8192*2
        # number of extracted data at a time,that is called chunk
        self.__chunk = 2**10
        # get device information
        self.__audio = pyaudio.PyAudio()
        # instance of stream obj for making wav file
        self.__stream = None
    
    def set_config(self, time_sec=3, outfile=["record.wav"], device_index=1, sampling_rate=44100, chunk=2**10, format=pyaudio.paInt16, nchannels=1):
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
    
    def show_deviceinfo(self):
        for i in range(self.__audio.get_device_count()):
            print(self.__audio.get_device_info_by_index(i))
    
    def get_audio_file_list(self):
        return self.__output_wavfile
    
    def record_voice(self, wfile_list=["record.wav"], dst="./control/audioSample/", overwrite=False) -> list:
        if dst[-1] != "/":
            print("Destination must be ended with \"/\"")
            raise NotADirectoryError

        makedirs(dst, exist_ok=True) # check if dst already exists. If doesn't, make new dir
        if overwrite == False and set.intersection(set(wfile_list), listdir(dst)) != set():
            print("Same wavfile exists in {0}\nYou were about to overwrite {1}\nIf you wouldn't mind it, set overwrite flag True".format(dst, dst+w))
            raise FileExistsError

        #audio.open() method returns a new Stream instance taking some arguments for configuration
        self.__stream = self.__audio.open(
            format = self.__format,
            channels = self.__nchannels,
            rate = self.__sampling_rate,
            input = True,
            input_device_index = self.__idevice, # device1(Mouse_mic) will be used for input device
            frames_per_buffer = self.__chunk
        )
        wtime = int(self.__sampling_rate / self.__chunk * self.__record_time)
        for w in wfile_list:
            print("Start recording...")
            frames = []
            for i in range(0, wtime):
                data = self.__stream.read(self.__chunk) # chunkごとにdataを書き出す write raw data at each chunk
                frames.append(data)
            print("Finished recording")

            self.__prepare_file(frames, dst+w)
            print("Output_file was generated\n")
        self.__output_wavfile = wfile_list
        self.__close_all()
        return self.__output_wavfile

#private methods          
    def __prepare_file(self, frames, wfile, mode='wb'):
        wavefile = wave.open(wfile, mode)
        wavefile.setnchannels(self.__nchannels)
        wavefile.setsampwidth(self.__audio.get_sample_size(self.__format))
        wavefile.setframerate(self.__sampling_rate)
        wavefile.writeframes(b"".join(frames))
        wavefile.close()
        return wfile

    def __close_all(self):
        self.__stream.close()
        self.__audio.terminate()
        print("pyaudio was terminated")

#end of class Recorder

if __name__ == "__main__":
    rc = Recorder()
    rc.record_voice(wfile_list=["a.wav"], overwrite=True)
#    with Recorder() as record:
#        fout = record.record_voice(wfile_list=["test"+str(w)+".wav" for w in range(3)], overwrite=True)