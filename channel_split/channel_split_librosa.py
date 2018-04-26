import librosa
import os
import time
import pyaudio
import numpy as np

project_path=os.getcwd()

st = time.time()
y, sr = librosa.load(project_path+'/resource/20180226_18678185232_2491531.mp3', mono=False, res_type='kaiser_fast')
# note: mono=False; y_data_format = [n dimensions](left_channel)[n dimensions](right_channel); check through debug
librosa.output.write_wav(project_path+'/resource/test_left.wav',np.array(y[0,:]),sr)
librosa.output.write_wav(project_path+'/resource/test_right.wav', np.array(y[1,:]),sr)
print time.time() - st