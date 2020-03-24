#!/usr/bin/env python

"""
This script encodes videos with variable segment durations.
"""

import re
import os, re, subprocess, sys

def encode_video(path_orig,fps,durations):
    proc_list = []
    for sec in durations:
        print(sec)
        g = int(sec * fps)
        min_g = 0
        sec_name = str(sec).replace('.','_')
        dir_path = 'var{sec_name}sec/'.format(**locals())
        path_out = dir_path + 'playlist.mpd'
        if not os.path.exists(dir_path): os.makedirs(dir_path)
        command = 'ffmpeg -i {path_orig} -nostats -threads 1 -vcodec libx264 -map 0:0 ' \
            '-x264-params keyint={g}:min-keyint={min_g} ' \
            '-use_timeline 1 -use_template 1 -hls_playlist 1 -seg_duration 0 ' \
            '-f dash {path_out} '.format(**locals()) 
        print(command)
        proc_list.append(subprocess.Popen(command.split()))
    for proc in proc_list:
        proc.wait()
    print('Finished!')

if __name__== "__main__":
    if len(sys.argv) < 3:
        print('Usage: python createVars.py [input] [framerate] [1,2,3,4,5(durations)]')
        exit()
    file_name = sys.argv[1]
    fps = float(sys.argv[2])
    input_durs = sys.argv[3]
    durations = map(float, input_durs.strip('[]').split(','))
    encode_video(file_name,fps,durations)
