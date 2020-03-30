# Video Scripts

1. [Create Reference Encoding](#Create-Reference-Encoding)
2. [Extract I-Frame Positions](#Extract-I-Frame-Positions)
3. [Generate VBR Job Files](#Generate-VBR-Job-Files)
4. [Generate CBR Job Files](#Generate-CBR-Job-Files)

## Create Reference Encoding
Create reference encodings manually or by using

    python createVars.py [input] [fps] [maxmimum-durations]

Specify for [maxmimum-durations] a list for the maximum segment duration lengths, i.e. `4,6,8,10`.

## Extract I-Frame Positions
Extract the timestamps of the I-frame positions by using

    python getTimeStamps.py [input m3u8] [fps] [sub]

Enable substraction of 1/4 frame duration by replacing `[sub]` with `true`. We use FFmpeg to extract the "best-effort-timestamps" of all I-frames that are at the beginning of a segment. To cope with floating point imprecision we subtract a small safety margin (1/4 frame duration). This ensures that the next frame after the adjusted timestamp is the frame which shall be encoded as I-frame. When using force key frame with this timestamp the next frame will be encoded as key frame.

## Generate VBR Job Files
Add the extracted I-frame timelines to the dictionary `[Bunny/Elfuente/Meridia/TearsOfSteel]_t_sub` in [generateJobs.py](generateJobs.py#L43-L97). Ignore the dictionaries with the exact timestamps.
It should follow this style:

| Max Duration | Timeline                                   |
|--------------|--------------------------------------------|
| 4            | "0.0,3.98958,4.40625,8.40625,..."          |
| 6            | "0.0,4.19791,10.19791,16.19791,..."        |
| 8            | "0.0,4.19791,12.19791,16.28125,..."        |
| 10           | "0.0,4.19791,14.19791,16.28125,..."        |

Add the maximum segment duration for all variable-length encodings in [generateJobs.py](generateJobs.py#L106-L111).

For the next step, you need to have the extracted average segment lengths of the variable-length encodings and round them to a precision of 0.5s. You can do this by first creating the variable-length encodings jobs `python generateJobs.py` and use the video docker to create the encodings and the video statistics files. Afterward, you can use

    grep -oP '"durations_mean":\s(\d+\.\d+)' video_statistics.json

to extract the average segment length of the corresponding encoding. If you did this, you can remove the durations for variable lengths from [generateJobs.py](generateJobs.py#L106-L111), otherwise, you will create those job files again in the next step.

Add the corresponding average lengths and the maximum lengths for the fixed lengths encodings in [generateJobs.py](generateJobs.py#L113-L118).
In the end, you can run

    python generateJobs.py

to create all variable bitrate jobs.

Add the job files to the working queue of the docker container and start the encoding process.

## Generate CBR Job Files
Use

    python extractCBRStats.py [DIR] [OUTPUT]

to extract needed bitrate information. The `[DIR]` input parameter should point to the [result directory](https://github.com/fg-inet/docker-video-encoding/blob/master/run_workers_mmsys.sh#L13) of the VBR Jobs.
The `[OUTPUT]` parameter should specify the output of the program as a JSON file, e.g. `cbr_jobs.json`.

Use

    python generateJobs.py cbr_jobs.json

to generate all constant bitrate encoding job files.