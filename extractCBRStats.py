#!/usr/bin/env python

"""
This script extracts information for constant bitrate encoding.
"""

import os, sys
import json
import jsonmerge
import bisect

# videos
videos = ['Bunny', 'ElFuente', 'Meridian', 'TearsOfSteel']

Bunny = [\
    'BigBuckBunny-240.avi',     # 2.4G  \
    'BigBuckBunny-480.avi',     # 7.9G  \
    'BigBuckBunny-720.avi',     # 15.5G \
    'BigBuckBunny-1080.avi',    # 30.1G \
    'BigBuckBunny-2160.avi'     # 92.7G \
    ]

ElFuente = [\
    'ElFuente-240.avi',     # 4.7G  \
    'ElFuente-480.avi',     # 17.1G \
    'ElFuente-720.avi',     # 36.1G \
    'ElFuente-1080.avi',    # 76.0G \
    'ElFuente-2160.avi'     # 294G  \
    ]

Meridian = [\
    'Meridian-240.avi',     # 2.7G  \
    'Meridian-480.avi',     # 10.9G \
    'Meridian-720.avi',     # 25.4G \
    'Meridian-1080.avi',    # 59.0G \
    'Meridian-2160.avi'     # 252G  \
    ]

TearsOfSteel = [\
    'TearsOfSteel-240.avi',     # 1.5G  \
    'TearsOfSteel-480.avi',     # 5.1G  \
    'TearsOfSteel-720.avi',     # 10.9G \
    'TearsOfSteel-1080.avi',    # 23.4G \
    'TearsOfSteel-2160.avi'     # 76.5G \
    ]

def round_bitrate(bitrate):
    return round(bitrate / 50000.0) * 50000.0

def round_05(number):
    return round(number * 2) / 2

# crf values
crfs = [16,22,28,34]

# maximum durations
max_durs = [4,6,8,10]

def get_results(path_to_results):
    print(path_to_results)
    results = {}
    results['var'] = {}
    results['fix'] = {}
    for (dirpath, dirnames, filenames) in os.walk(path_to_results):
        for filename in filenames:
            base = None
            if filename == 'video_statistics.json':
                try:
                    with open(os.sep.join([dirpath, 'video_statistics.json'])) as f:
                        vid_statistics = json.load(f)
                        base = jsonmerge.merge(base, vid_statistics)
                    with open(os.sep.join([dirpath, 'vid_opts.json'])) as f:
                        vid_opts = json.load(f)
                        vid_opts['crf'] = vid_opts['crf_vals'][0]
                        base = jsonmerge.merge(base, vid_opts)
                    with open(os.sep.join([dirpath, 'stats.json'])) as f:
                        stats = json.load(f)
                        base = jsonmerge.merge(base, stats)
                    with open(os.sep.join([dirpath, 'timings.json'])) as f:
                        timings = json.load(f)
                        base = jsonmerge.merge(base, timings)
                    with open(os.sep.join([dirpath, 'vid_stats.json'])) as f:
                        stats = json.load(f)
                        base = jsonmerge.merge(base, stats)
                    
                    # check fps
                    if base['fps'] != 24:
                        print("Found other", base['fps'])
                        continue
                    
                    if base['job_dict']['target_seg_length'] == 0:
                        enc_ = 'var'
                    else:
                        enc_ = 'fix'
                        continue

                    if not base['steady_id'] in results[enc_]:
                        results[enc_][base['steady_id']] = {}
                    if not base['steady_id'] in results['fix']:
                        results['fix'][base['steady_id']] = {}
                    if not int(vid_opts['crf']) in results[enc_][base['steady_id']]:
                        results[enc_][base['steady_id']][int(vid_opts['crf'])] = []
                    if not int(vid_opts['crf']) in results['fix'][base['steady_id']]:
                        results['fix'][base['steady_id']][int(vid_opts['crf'])] = []

                    max_length = float(base['job_dict']['max_length'])
                    mean_bitrate = round_bitrate(float(base['bitrate_mean']))

                    if not max_length in results[enc_][base['steady_id']][int(vid_opts['crf'])]:
                        bisect.insort(results[enc_][base['steady_id']][int(vid_opts['crf'])],(max_length,mean_bitrate))
                        bisect.insort(results['fix'][base['steady_id']][int(vid_opts['crf'])],(max_length,mean_bitrate))
                        # add mean durations as job
                        dur_round = round_05(float(base['durations_mean']))
                        bisect.insort(results['fix'][base['steady_id']][int(vid_opts['crf'])],(dur_round,mean_bitrate))
                except:
                    pass
    return results

if __name__== "__main__":
    if len(sys.argv) < 2:
        print('Usage: python extractCBRStats.py [DIR] [OUTPUT]')
        exit()
    input_dir = str(sys.argv[1])
    results = get_results(input_dir)
    print(results)
    if len(sys.argv) > 2:
        output_file = str(sys.argv[2])
        with open(output_file, 'w') as fp:
            json.dump(results, fp)
    
