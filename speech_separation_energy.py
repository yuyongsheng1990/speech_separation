import os
import math
import wave
import glob
import time
from pydub.audio_segment import AudioSegment
import numpy as np

project_path = os.getcwd()
st = time.time()

# transfer time format
def time_format(seconds):
    # time_round = round(seconds, 2)
    # return str(time_round)
    hour_time = math.floor(seconds/3600)
    minute_time = math.floor((seconds - hour_time*3600)/60)
    second_time = round(seconds - hour_time*3600 - minute_time*60,2)
    time = str(int(hour_time))+':'+str(int(minute_time))+':'+str(second_time)
    return time

# get left_endpoint
def left_point(index,sum):
    while index <= len(sum) - 1:
        if index == len(sum) - 1:
            global exit_value
            exit_value = True
            return index
        elif sum[index] == 0 and sum[index + 1] > 0:
            return index
        elif index == len(sum):
            exit_value =True
            return index - 1
        index += 1


# get right_endpoint
def right_point(index,sum):
    while index <= len(sum) - 1:
        if index == len(sum) - 1:
            global exit_value
            exit_value = True
            return index
        elif sum[index] > 0 and sum[index + 1] == 0:
            return index
        elif index == len(sum):
            exit_value = True
            return index - 1
        index += 1

# detect speech point
def speech_separate(wave_data):
    # change wave data to array data
    time = np.arange(0, nframes) * (1.0 / framerate)

    # normalized and filter noise
    data = []
    maxvalue = max(wave_data)
    for i in xrange(len(wave_data)):
        tt = (wave_data[i] * 1.0) / maxvalue
        if abs(tt) > 0.1:
            data.append(tt)
        else:
            data.append(0)

    # break point detection based on energy and zero
    windows = framerate / 200
    windows_time = windows * (1.0 / framerate)
    energy = []
    zero = []
    for i in xrange(int(len(time) / windows)):
        # energy
        win_data = data[windows * i: windows * (i + 1)]
        win_data_flo = np.array(win_data, dtype=np.float)
        en = np.dot(win_data_flo, win_data_flo.T)
        if en < 0:
            print win_data_flo
            exit()
        energy.append(en)
        # zero
        count = 0
        base = i * windows
        for j in xrange(windows):
            if (data[base + j] > 0 and data[base + j + 1] < 0) or (data[base + j] < 0 and data[base + j + 1] > 0):
                count = count + 1
        zero.append(count)
    # integrate energy and zero
    maxzero = max(zero)
    zerodata = []
    for i in xrange(len(zero)):
        zerodata.append((zero[i] * 1.0) / maxzero)
    sum = []
    for i in xrange(len(zerodata)):
        sum.append(zerodata[i] + energy[i])

    i = 0
    while i <= len(sum) - 1:
        left_tem = left_point(i,sum)
        if exit_value: break # the last sum[i] is at the period of detecting left point, left_tem = len(sum)-1.
        ''' ν	如果上一个暂时左端点last_nextleft_tem为0，这说明上一个left端点将语音数据全部输出了，程序end；
            ν	否则，程序没有检测到合适的left端点，程序输出sum[last_nextleft_tem:]，程序end。
            if nextleft_tem == len(sum)-1:
                break
            else:
                left =nextleft_tem
                right = len(sum) -1
                file.writelines(str(num) + ',' + str(time_format(time[left * windows])) + ',' + str(
                    time_format(time[right * windows])) + '\n')
                # output .wav audio
                fw = wave.open(
                    project_path + '/speech_separation/' + os.path.splitext(os.path.basename(test_speech))[0] +
                    '_' + str(num) + '_' + str(time_format(time[left * windows])) + ' : ' +
                    str(time_format(time[right * windows])) + '.wav', 'wb')
                fw.setnchannels(1)
                fw.setsampwidth(sampwidth)
                fw.setframerate(framerate)
                fw.writeframes(wave_data[left * windows:right * windows].tostring())
                fw.close()
                break'''
        right_tem = right_point(left_tem + 1, sum)
        # if the last sum[i] is at the period of detecting right point. rigth_tem = len(sum)-1 and exit_value=true
        if exit_value or (right_tem - left_tem) * windows_time >= 0.2:
            left = left_tem
            # get right point
            j = right_tem
            while j <= len(sum) - 1:
                right_tem = right_point(j, sum) # if the last sum[i] is at the period of detecting right.
                nextleft_tem = left_point(right_tem + 1, sum)
                if exit_value or (nextleft_tem - right_tem) * windows_time > 0.5:
                    right = right_tem
                    file.writelines(str(num)+','+str(time_format(time[left*windows]))+','+str(time_format(time[right*windows]))+'\n')
                    # output .wav audio
                    fw = wave.open(project_path + '/speech_separation/' +os.path.splitext(os.path.basename(test_speech))[0]+
                                   '_'+str(num)+'_'+str(time_format(time[left * windows])) + ' : ' +
                                   str(time_format(time[right * windows])) + '.wav', 'wb')
                    fw.setnchannels(1)
                    fw.setsampwidth(sampwidth)
                    fw.setframerate(framerate)
                    fw.writeframes(wave_data[left * windows:right * windows].tostring())
                    fw.close()
                    i = nextleft_tem - 1
                    break
                j = right_tem + 1
        i = i + 1

if __name__ == '__main__':
    # input mono channel wav file
    os.chdir(project_path+'/resource/')
    for test_speech in glob.glob('*.mp3'):
        fr = AudioSegment.from_mp3(test_speech)
        framerate, nframes, sampwidth =fr.frame_rate, fr.frame_count(), fr.sample_width
        index = fr.split_to_mono()
        num = 1
        # output  record
        file = open(project_path + '/speech_separation/' + os.path.splitext(os.path.basename(test_speech))[0]+'.txt', 'w')
        for mp3_data in index:
            exit_value = False
            mp3_data_array = mp3_data.get_array_of_samples()
            # wave_data = np.fromstring(mp3_data_array, dtype=np.short)
            speech_separate(mp3_data_array)
            num += 1
        file.close()
        print(time.time() - st)