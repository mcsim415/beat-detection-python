from __future__ import unicode_literals
import os
import re
import sys
import time
import wave
import wavio
import random
import librosa
import pyaudio
import soundfile
import youtube_dl
import numpy as np
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import urlopen


custom_detection = True
default_max = 9
sub_bass_max = default_max
bass_max = default_max
low_midrange_max = default_max
midrange_max = default_max
upper_midrange_max = default_max
presence_max = default_max
brilliance_max = default_max
high_max = default_max

sub_bass_beat = False
bass_beat = False
low_midrange_beat = False
midrange_beat = False
upper_midrange_beat = False
presence_beat = False
brilliance_beat = False
high_beat = False

current_time = 0
# High is easy
# 1 - INSANE
# 2 - Hard
# 3 - Normal (Default)
# 4 - Easy
# 5 - VERY EASY
level = 3


def download_from_youtube(yid):
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': yid + '.wav',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['http://www.youtube.com/watch?v=' + yid])


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def analyze(arg, result_callback):
    try:
        if os.path.isfile(arg):
            filename = arg
            wf = wave.open(filename, 'rb')
        elif uri_validator(arg):
            url = arg
            youtube = re.compile(
                'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?').match(url)
            if youtube:
                youtube_id = youtube.groups()[0]
                filename = youtube_id + ".wav"
                if os.path.exists(filename):
                    wf = wave.open(filename, 'rb')
                else:
                    youtube_test_url = "https://img.youtube.com/vi/" + youtube_id + "/mqdefault.jpg"
                    res = urllib.request.urlopen(youtube_test_url)
                    valid = False
                    try:
                        res = urlopen(url)
                        print(res.status)
                        valid = True
                    except HTTPError:
                        valid = False

                    if not valid:
                        print("Not valid youtube link")
                        sys.exit(-1)
                    else:
                        download_from_youtube(youtube_id)
                        filename = youtube_id + ".wav"
                        wf = wave.open(filename, 'rb')
            else:
                filename = url.strip().split('/')[-1]
                urllib.request.urlretrieve(url, filename)
                wf = wave.open(filename, 'rb')
        else:
            print("Plays a wave file.\n\nUsage: %s filename.wav\nOr youtube link Or wav file link" % sys.argv[0])
            sys.exit(-1)
    except wave.Error:
        print("File is crashed. Auto change to wav.")
        x, _ = librosa.load(filename, sr=48000)
        soundfile.write(filename, x, 48000)
        wf = wave.open(filename, 'rb')

    fs = wf.getframerate()
    channels = wf.getnchannels()
    bytes_per_sample = wf.getsampwidth()
    print(wf.getframerate())
    p = pyaudio.PyAudio()


    def beat2game(beat_id):
        global current_time, level
        seed = current_time * beat_id
        random.seed(seed)
        passing = random.randrange(0, level)

        arrow_type = random.randrange(0, 7)
        if arrow_type == 0:
            arrow_type = 0
        else:
            arrow_type = 1
        direction = random.randrange(1, 5)
        pattern = random.randrange(1, 6)

        result_callback(passing, arrow_type, direction, pattern, current_time)


    # Beat Detection Algo
    def beat_detect(in_data):
        audio = wavio._wav2array(channels, bytes_per_sample, in_data)

        audio_fft = np.abs((np.fft.fft(audio)[0:int(len(audio) / 2)]) / len(audio))
        freqs = fs * np.arange(len(audio) / 2) / len(audio)

        sub_bass_indices = [idx for idx, val in enumerate(freqs) if 20 <= val <= 60]
        bass_indices = [idx for idx, val in enumerate(freqs) if 60 <= val <= 250]
        low_midrange_indices = [idx for idx, val in enumerate(freqs) if 250 <= val <= 500]
        midrange_indices = [idx for idx, val in enumerate(freqs) if 500 <= val <= 2000]
        upper_midrange_indices = [idx for idx, val in enumerate(freqs) if 2000 <= val <= 4000]
        presence_indices = [idx for idx, val in enumerate(freqs) if 4000 <= val <= 6000]
        brilliance_indices = [idx for idx, val in enumerate(freqs) if 6000 <= val <= 20000]
        high_indices = [idx for idx, val in enumerate(freqs) if 20000 <= val <= 100000]

        sub_bass = np.max(audio_fft[sub_bass_indices])
        bass = np.max(audio_fft[bass_indices])
        low_midrange = np.max(audio_fft[low_midrange_indices])
        midrange = np.max(audio_fft[midrange_indices])
        upper_midrange = np.max(audio_fft[upper_midrange_indices])
        presence = np.max(audio_fft[presence_indices])
        brilliance = np.max(audio_fft[brilliance_indices])
        high = np.max(audio_fft[high_indices])

        global sub_bass_max, bass_max, low_midrange_max, midrange_max, \
            upper_midrange_max, presence_max, brilliance_max, high_max
        global sub_bass_beat, bass_beat, low_midrange_beat, midrange_beat, \
            upper_midrange_beat, presence_beat, brilliance_beat, high_beat
        global custom_detection

        if not custom_detection:
            sub_bass_max = max(sub_bass_max, sub_bass)
            bass_max = max(bass_max, bass)
            low_midrange_max = max(low_midrange_max, low_midrange)
            midrange_max = max(midrange_max, midrange)
            upper_midrange_max = max(upper_midrange_max, upper_midrange)
            presence_max = max(presence_max, presence)
            brilliance_max = max(brilliance_max, brilliance)
            high_max = max(high_max, high)

        b2g = 0

        if sub_bass >= sub_bass_max * .9 and not sub_bass_beat:
            sub_bass_beat = True
            b2g += 1
        elif sub_bass < sub_bass_max * .3:
            sub_bass_beat = False

        if bass >= bass_max * .9 and not bass_beat:
            bass_beat = True
            b2g += 2
        elif bass < bass_max * .3:
            bass_beat = False

        if low_midrange >= low_midrange_max * .9 and not low_midrange_beat:
            low_midrange_beat = True
            b2g += 3
        elif low_midrange < low_midrange_max * .3:
            low_midrange_beat = False

        if midrange >= midrange_max * .9 and not midrange_beat:
            midrange_beat = True
            b2g += 4
        elif midrange >= midrange_max * .3:
            midrange_beat = False

        if upper_midrange >= upper_midrange_max * .9 and not upper_midrange_beat:
            upper_midrange_beat = True
            b2g += 5
        elif upper_midrange < upper_midrange_max * .3:
            upper_midrange_beat = False

        if presence >= presence_max * .9 and not presence_beat:
            presence_beat = True
            b2g += 6
        elif presence < presence_max * .3:
            presence_beat = False

        if brilliance >= brilliance_max * .9 and not brilliance_beat:
            brilliance_beat = True
            b2g += 7
        elif brilliance < brilliance_max * .3:
            brilliance_beat = False

        if high >= high_max * .9 and not high_beat:
            high_beat = True
            b2g += 8
        elif high < high_max * .3:
            high_beat = False

        if not b2g == 0:
            beat2game(b2g)

        # primary_freq = freqs[np.argmax(audio_fft)]
        # print("Primary Frequency: ", freqs)
        # primary_freq = np.argmax(audio_fft)


    # define callback (2)
    def callback(in_data, frame_count, time_info, status):
        global current_time
        current_time += 1
        data = wf.readframes(frame_count)
        beat_detect(data)
        return data, pyaudio.paContinue


    # open stream using callback (3)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    # start the stream (4)
    stream.start_stream()

    # wait for stream to finish (5)
    while stream.is_active():
        time.sleep(0.1)

    # stop stream (6)
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio (7)
    p.terminate()
