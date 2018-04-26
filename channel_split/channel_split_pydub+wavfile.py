import os
import time
import glob
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment

project_path = os.getcwd()

st = time.time()
# function: wavfile slit speech to two channels
def splitChannel(speechfile):
    sampleRate, speechdata =wavfile.read(speechfile)
    # speechdata_format=[[left_channel,right_channel][left_channel,right_channel]](n dimensions)
    left=[]
    right=[]
    for item in speechdata:
        left.append(item[0])
        right.append(item[1])
    # wavfile.write(project_path+'/resource/test_left.wav',sampleRate,np.array(le)
    # wavfile.write(project_path+'/resource/test_right.wav', sampleRate, np.array(right))
#pydub transform mp3 to wav
os.chdir(project_path+'/speech_separate_data')
for file in glob.glob('*.mp3'):
    sound = AudioSegment.from_mp3(file)
    sound.export(project_path+'/speech_separate_data/'+os.path.splitext(os.path.basename(file))[0]+'.wav', format='wav')
# splitChannel(project_path+'/resource/test.wav')
print time.time()-st