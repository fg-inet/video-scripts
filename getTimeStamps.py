#!/usr/bin/env python

"""
This script allows to get the frametimes from a m3u8 file.
It substracts 1/4 from the framerate. If you insert a keyframe
using the forcekeyframe options ffmpeg sets it to the next frame.
Substracting an offset should help that ffpmeg proccesses this correctly.
"""

import os, sys, re, time, json
import subprocess
import numpy as np
import math

def get_vid_stream_stats(file_name):
    command = 'ffprobe -show_entries frame -show_streams ' \
            '-print_format json -show_entries frame ' \
            '-i {file_name}'.format(file_name=file_name)
    #print(command)
    proc = subprocess.Popen(command.split(), \
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = proc.communicate()
    json_dump = json.loads(stderr[0].decode('utf-8'))
    times = []
    print(len(json_dump['frames']))
    frames = json_dump['frames']
    for frame in frames:
        frame_type = frame['pict_type']
        if frame_type == 'I':
            times.append(float(frame['best_effort_timestamp_time']))
    return times, frames

def get_timeline(input_file):
    timeline_I,frames = get_vid_stream_stats(input_file)
    timeline = [0]
    count = 1
    with open(input_file,'r') as m3u8:
        for line in m3u8:
            if line.startswith('#EXTINF:'):
                duration = float(line.replace('#EXTINF:','').split(',')[0])
                stamp = timeline[count-1] + duration

                idx = (np.abs(np.array(timeline_I) - stamp)).argmin()
                timeline.append(timeline_I[idx])                

                count += 1
    return timeline[:-1] # remove last element

def process_timeline(timeline, frame_sub_offset):
    out = ''
    i = 0
    for t in timeline:
        if (t-frame_sub_offset) < 0:
            stamp = 0
        else:
            stamp = t-frame_sub_offset
        if i == 0:
            out +=  str(truncate(stamp,5))
        else:
            out += ',' + str(truncate(stamp,5))
        i += 1
    return out

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

if __name__== "__main__":
    if len(sys.argv) < 2:
        print('Usage: python getTimeStamps.py [input m3u8] [framerate] [SUB]')
        exit()
    input_file=str(sys.argv[1])
    framerate=float(sys.argv[2])
    sub_frame_t = (1/(framerate*4))
    timeline = get_timeline(input_file)

    if len(sys.argv) > 3:
        sub_frame  = str2bool(sys.argv[3])
        if sub_frame  == True:    
            print(process_timeline(timeline, sub_frame_t))
        else:
            print(process_timeline(timeline, 0.0))
    else:
        # just both
        print(process_timeline(timeline, sub_frame_t))
        print()
        print(process_timeline(timeline, 0))
