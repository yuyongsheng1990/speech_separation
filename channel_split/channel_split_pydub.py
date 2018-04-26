# _*_ coding: utf-8 _*_
# @Time     : 2018/4/19 下午3:42
# @Author   : yu yongsheng
# @FileName : channel_split_pydub2.py.py
# @Software :
# @Description: split_channel_pydub

import os
import time
import glob
import numpy as np
from pydub.audio_segment import AudioSegment

project_path=os.getcwd()

st=time.time()

os.chdir(project_path+'/speech_separate_data/')
for path in glob.glob('*.mp3'):
    print path
    mp3_file = AudioSegment.from_mp3(path)
    # mp3_file = mp3_file.set_frame_rate(22050)
    # each index in split_to_mono() represent a channel(0-left/1-right)
    index = mp3_file.split_to_mono()
    index[0].export(project_path + "/channel_data/" + os.path.splitext(os.path.basename(path))[0]+ '_left.wav',format="wav")
    index[1].export(project_path + "/channel_data/" + os.path.splitext(os.path.basename(path))[0]+'_right.wav',format="wav")
print time.time() - st