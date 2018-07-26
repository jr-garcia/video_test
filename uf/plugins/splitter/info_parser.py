import datetime
import os
import re
import time
from subprocess import PIPE, DEVNULL, Popen


def ffmpeg_parse_infos(filename, print_infos=False, check_duration=True, fps_source='tbr'):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_nframes",
    "video_duration", "audio_found", "audio_fps"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """

    # open the file in a pipe, provoke an error, read output
    cmd = ['ffmpeg', "-i", filename]

    popen_params = {"bufsize": 10 ** 5, "stdout": PIPE, "stderr": PIPE, "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = Popen(cmd, **popen_params)

    proc.stdout.readline()
    proc.terminate()
    infos = proc.stderr.read().decode('utf8')
    del proc

    if print_infos:
        # print the whole info text returned by FFMPEG
        print(infos)

    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError(("the file %s could not be found!\n"
                       "Please check that you entered the correct "
                       "path.") % filename)

    result = dict()

    # get duration (in seconds)
    result['duration'] = None

    if check_duration:
        try:
            keyword = 'Duration: '
            index = 0
            line = [l for l in lines if keyword in l][index]
            match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
            result['duration'] = convertTime(match)
        except Exception as Ex:
            raise IOError((str(Ex) + " failed to read the duration of file %s.\n"
                                     "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

    # get the output line that speaks about video
    lines_video = [l for l in lines if ' Video: ' in l and re.search('\d+x\d+', l)]

    result['video_found'] = (lines_video != [])

    if result['video_found']:
        try:
            line = lines_video[0]

            # get the size, of the form 460x320 (w x h)
            match = re.search(" [0-9]*x[0-9]*([, ])", line)
            s = tuple(map(int, line[match.start():match.end() - 1].split('x')))
            result['video_size'] = s
        except Exception:
            raise IOError(("failed to read video dimensions in file %s.\n"
                           "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust tbr first, then fps unless fps_source is
        # specified as 'fps' in which case try fps then tbr

        # If result is near from x*1000/1001 where x is 23,24,25,50,
        # replace by x*1000/1001 (very common case for the fps).

        def get_tbr():
            match = re.search("( [0-9]*.| )[0-9]* tbr", line)

            # Sometimes comes as e.g. 12k. We need to replace that with 12000.
            s_tbr = line[match.start():match.end()].split(' ')[1]
            if "k" in s_tbr:
                tbr = float(s_tbr.replace("k", "")) * 1000
            else:
                tbr = float(s_tbr)
            return tbr

        def get_fps():
            match = re.search("( [0-9]*.| )[0-9]* fps", line)
            fps = float(line[match.start():match.end()].split(' ')[1])
            return fps

        if fps_source == 'tbr':
            try:
                result['video_fps'] = get_tbr()
            except Exception:
                result['video_fps'] = get_fps()

        elif fps_source == 'fps':
            try:
                result['video_fps'] = get_fps()
            except Exception:
                result['video_fps'] = get_tbr()

        # It is known that a fps of 24 is often written as 24000/1001
        # but then ffmpeg nicely rounds it to 23.98, which we hate.
        coef = 1000.0 / 1001.0
        fps = result['video_fps']
        for x in [23, 24, 25, 30, 50]:
            if (fps != x) and abs(fps - x * coef) < .01:
                result['video_fps'] = x * coef

        if check_duration:
            result['video_nframes'] = int(result['duration'] * result['video_fps']) + 1
            result['video_duration'] = result['duration']
        else:
            result['video_nframes'] = 1
            result['video_duration'] = None
        # We could have also recomputed the duration from the number
        # of frames, as follows:
        # >>> result['video_duration'] = result['video_nframes'] / result['video_fps']

        # get the video rotation info.
        try:
            rotation_lines = [l for l in lines if 'rotate          :' in l and re.search('\d+$', l)]
            if len(rotation_lines):
                rotation_line = rotation_lines[0]
                match = re.search('\d+$', rotation_line)
                result['video_rotation'] = int(rotation_line[match.start(): match.end()])
            else:
                result['video_rotation'] = 0
        except Exception:
            raise IOError(("failed to read video rotation in file %s.\n"
                           "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

    lines_audio = [l for l in lines if ' Audio: ' in l]

    result['audio_found'] = lines_audio != []

    if result['audio_found']:
        line = lines_audio[0]
        try:
            match = re.search(" [0-9]* Hz", line)
            result['audio_fps'] = int(line[match.start() + 1:match.end()])
        except Exception:
            result['audio_fps'] = 'unknown'

    return result


def convertTime(timeStr):
    # https://stackoverflow.com/a/10663851
    main, remain = timeStr.split('.')
    x = time.strptime(main, '%H:%M:%S')
    res = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    return res + float('.' + remain)