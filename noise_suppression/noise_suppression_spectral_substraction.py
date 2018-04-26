# _*_ coding: utf-8 _*_
# @Time     : 2018/4/23 上午9:40
# @Author   : yu yongsheng
# @FileName : noise_suppression_spectral_substraction.py
# @Software :
# @Description:

import os
import wave
import math
import time
import numpy as np

project_path = os.getcwd()

st = time.time()

# Find 2^n that is equal to or greater than x and return n.
def nextpow2(x): # This is internal function used by fft(), because the FFT routine requires that the data size be a power of 2.
    exponent = 1
    n = 1
    while n < x:
        exponent += 1
        n = 2 ** (exponent-1)
    return exponent

def alpha_compute(SNR_value): # compute alpha_value when power exponent isn't 1
    if -5.0 <= SNR_value <= 20.0:
        a = 4 - SNR_value * 3/20
    else:
        if SNR_value < -5.0:
            a = 5
        if SNR_value > 20.0:
            a =1
    return a

def alpha_compute1(SNR_value): # compute alpha_value when power exponent is 1.
    if -5.0 <= SNR_value <= 20.0:
        a = 3 - SNR_value * 2/20
    else:
        if SNR_value < -5.0:
            a = 4
        if SNR_value > 20.0:
            a =1
    return a

def beta_compute(SNR_value): # compute beta_value according to SNR_value
    if SNR_value < -5.0:
        b = 0.06
    elif SNR_value > 20:
        b = 0.005
    else:
        b = 0.06 - 0.055 * (SNR_value+5)/ 25
    return b

def diff_negative_value_count(diff_value):
    negvalue_list=[]
    for i in range(len(diff_value)):
        if diff_value[i] <0:
            negvalue_list.append(i)
    return negvalue_list

if __name__ == '__main__':
    # input file
    fr = wave.open(project_path + '/audio_data/20180302_13922316522_2813750.wav')
    params = fr.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = fr.readframes(nframes)
    wave_data = np.fromstring(str_data, dtype=np.short)
    fr.close()

    # compute parameters
    win_len = 20 * framerate // 100  # the length of hamming window
    overlap_percent = 50  # the percent of window overlap
    len1 = win_len * overlap_percent // 100  # the overlap length of window, 50%  = 50//100
    len2 = win_len - len1  # the un-overlap length of hamming window

    # set the default params
    thres = 3  # the VAD threshold in SNR
    expnt = 2.0
    G = 0.9

    # construct a hamming window for noise suppression; assuming that the first 5 frames is noise/silence
    win = np.hamming(win_len)
    win_gain = len2 / sum(win)  # normalization gain for overlap and add with 50% overlap
    # win * wave_data[0:win_len] return an array

    # estimate the noise (noise_mu)
    fft_size = 2 * 2 ** nextpow2(win_len)
    noise_value = np.zeros(fft_size)  # construct an zero array to storage the noise data
    j = 0
    for k in range(1, 6):
        noise_value = noise_value + abs(np.fft.fft(win * wave_data[j:j + win_len],
                                                   fft_size))  # fft trans time signal to frequency signal, len gets longer
        j = j + win_len
    noise_mu = noise_value / 5

    # before noise suppression, initialize some variables
    wave_data_old = np.zeros(len1)
    img = 1j  # plural number
    nwindows = len(wave_data) // len2 - 1  # the num of overlap-window
    wave_data_final = np.zeros(
        nwindows * len2)  # state an final wave_data_list to save final pure_speech data, which length is equal to raw wave_data.

    # start process noise
    # iter_num=0
    k = 0
    for n in range(0, nwindows):
        # compute the frequency data of speech with noise
        speech_noise = win * wave_data[k: k + win_len]
        speech_noise_fft = np.fft.fft(speech_noise,
                                      fft_size)  # compute the fft-value of speech_noise, the frequency signal data, len is fft_size
        speech_noise_fft_abs = abs(speech_noise_fft)
        # save the phase information 相位信息
        theta = np.angle(speech_noise_fft)  # compute the phase angle
        SNR_value = 10 * np.log10(
            (np.linalg.norm(speech_noise_fft_abs, 2) ** 2) / (np.linalg.norm(noise_mu, 2) ** 2))  # compute SNR

        # compute the pure signal
        if expnt == 1.0:
            alpha = alpha_compute1(SNR_value)
        else:
            alpha = alpha_compute(SNR_value)
        speech_noise_power = speech_noise_fft_abs ** expnt
        noise_mu_power = noise_mu ** expnt
        pure_speech = speech_noise_power - alpha * noise_mu_power
        # compare pure speech and noisy signal to ns
        beta = beta_compute(SNR_value)
        diff_value = pure_speech - beta * noise_mu_power
        diff_negvalue_list = diff_negative_value_count(diff_value)
        if len(diff_negvalue_list) > 0:
            pure_speech[diff_negvalue_list] = beta * noise_mu[diff_negvalue_list] ** expnt
            # -------implement a simple VAD detect to update noise spectral--------------
            if SNR_value < thres:
                noise_temp = G * noise_mu_power + (1 - G) * speech_noise_power  # smoothing noise power
                noise_mu = noise_temp ** (1 / expnt)  # a new noise spectral # a new noise power
        # transform frequency signal to time signal-ifft, phase information of input signal
        pure_speech[fft_size // 2 + 1:fft_size] = np.flipud(
            pure_speech[1:fft_size // 2])  # flip array in up/down direction
        # the phase data of pure_speech_fft information
        wave_data_phase = (pure_speech ** (1 / expnt)) * (
                    np.array([math.cos(x) for x in theta]) + img * (np.array([math.sin(x) for x in theta])))
        # take the ifft
        wave_data_ifft = np.fft.ifft(wave_data_phase).real
        # export frequency data---overlap and add----
        wave_data_test = wave_data_ifft[0:len1]
        wave_data_final[k:k + len2] = wave_data_old + wave_data_ifft[0:len1]
        wave_data_old = wave_data_ifft[len1:win_len]  # compute frequency signal, add the overlap section
        k += len2
        # iter_num +=1
        # print(iter_num)

    print(time.time() - st)
    # output .wav file
    fw = wave.open(project_path + '/audio_data/test_ns.wav', 'wb')
    fw.setparams(params)  # set the default params
    wave_data_output = (win_gain * wave_data_final).astype(np.short)
    fw.writeframes(wave_data_output.tostring())
    fw.close()