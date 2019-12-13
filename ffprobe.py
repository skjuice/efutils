# -*- coding: utf-8 -*-
# above is to fix the error syntaxError: Non-ASCII character '\xc2' in file audit.py on line n

import os
import fs_utils as fileio
import sys
import subprocess
import logging
import shlex
import ushlex
import json
from pprint import pprint

suffix = None
ffprobe_suitable_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".mov", ".mp4", ".ts", ".mpg", ".mpeg", ".mkv", ".mxf", ".wav", ".avi", ".mp2", ".mp3", ".scc", ".srt", ".stl"]
hardcoded_ffprobe_path = None
debug = True
logger = logging.getLogger("media")

'''

This module is for python 2.7
For python3, use ffprobe3.py

'''
def gather_media_info(file, hash=True):

    file_attributes = {}
    duration = None
    frame_rate = None
    audio_channel_count = 0
    audio_track_count = 0
    filename, file_extension = os.path.splitext(file)

    #Skip hidden files. This logic should be put into get_files method. basename will give the filename with extension only
    if os.path.basename(file.decode('utf-8')).startswith('.'):
        return file_attributes

    file_attributes['file_path'] = file.decode("utf-8")
    file_attributes['file_name'] = os.path.basename(file).decode("utf-8") #filename with extension
    file_attributes['containing_dir'] = os.path.dirname(file).decode("utf-8")
    file_attributes['file_extension'] = file_extension[1:].lower().decode("utf-8")  #if file_extension was '.scc', then this would give 'scc'
    file_attributes['file_size'] = os.path.getsize(file)
    file_attributes['ffprobed'] = False

    # If file size is less than the defined size for running checksum on, then hash it
    if hash is True:
        file_attributes['md5'] = fileio.md5(file)
    else:
        file_attributes['md5'] = None

    if file_extension.lower() in ffprobe_suitable_extensions:
        file_attributes['ffprobed'] = True

        json_data = ffprobe_file(file)
        data = json.loads(json_data)    #data is a dictionary

        if data is not None:

            try:
                file_attributes['ffprobed_size'] = int(data['format']['size'])
            except (KeyError, TypeError) as e:
                file_attributes['ffprobed_size'] = ''

            try:
                file_attributes['bitrate'] = data['format'].get('bit_rate')
            except (KeyError, AttributeError):
                #AttributeError: 'NoneType' object has no attribute 'get'
                file_attributes['bitrate'] = ''

            try:
                file_attributes['duration'] = float(data.get('format').get('duration'))
            except (AttributeError, TypeError) as e:
                # TypeError because float() argument must be a string or a number
                file_attributes['duration'] = ''

            if 'streams' in data:
                file_attributes['has_streams'] = True
                file_attributes['streams'] = []

                for stream in data.get('streams'):

                    stream_data = {}
                    stream_data['codec_type']           = stream.get('codec_type').decode("utf-8") if stream.get('codec_type') else stream.get('codec_type')    #ternary stmt in python
                    stream_data['codec_name']           = stream.get('codec_name').decode("utf-8") if stream.get('codec_name') else stream.get('codec_name')
                    stream_data['codec_long_name']      = stream.get('codec_long_name').decode("utf-8") if stream.get('codec_long_name') else stream.get('codec_long_name')
                    stream_data['codec_tag']            = stream.get('codec_tag').decode("utf-8") if stream.get('codec_tag') else stream.get('codec_tag')
                    stream_data['codec_tag_string']     = stream.get('codec_tag_string').decode("utf-8") if stream.get('codec_tag_string') else stream.get('codec_tag_string')
                    stream_data['codec_time_base']      = stream.get('codec_time_base').decode("utf-8") if stream.get('codec_time_base') else stream.get('codec_time_base')

                    stream_data['avg_frame_rate']       = stream.get('avg_frame_rate')

                    if stream.get('codec_type') == 'video':
                        frame_rate                      = stream.get('avg_frame_rate')

                    stream_data['r_frame_rate']         = stream.get('r_frame_rate')
                    stream_data['nb_frames']            = stream.get('nb_frames')
                    stream_data['bit_rate']             = stream.get('bit_rate')
                    stream_data['max_bit_rate']         = stream.get('max_bit_rate')
                    stream_data['bits_per_raw_sample']  = stream.get('bits_per_raw_sample')
                    stream_data['bits_per_sample']      = stream.get('bits_per_sample')
                    stream_data['sample_rate']          = stream.get('sample_rate')
                    stream_data['sample_fmt']           = stream.get('sample_fmt')

                    stream_data['width']                = stream.get('width')
                    stream_data['height']               = stream.get('height')
                    stream_data['coded_width']          = stream.get('coded_width')
                    stream_data['coded_height']         = stream.get('coded_height')
                    stream_data['sample_aspect_ratio']  = stream.get('sample_aspect_ratio')
                    stream_data['display_aspect_ratio'] = stream.get('display_aspect_ratio')

                    stream_data['duration']             = stream.get('duration')

                    if stream.get('codec_type') == 'video':
                        duration                        = stream.get('duration')

                    stream_data['duration_ts']          = stream.get('duration_ts')
                    stream_data['field_order']          = stream.get('field_order')

                    stream_data['channel_layout']       = stream.get('channel_layout')
                    stream_data['channels']             = stream.get('channels')

                    if stream.get('codec_type') == 'audio':
                        audio_track_count = audio_track_count + 1

                    if stream.get('codec_type') == 'audio' and stream.get('channels'):
                        audio_channel_count                        = audio_channel_count + int(stream.get('channels'))

                    if stream.get('tags') and stream.get('tags').get('handler_name'):
                        stream_data['handler_name']     = stream.get('tags').get('handler_name')

                    file_attributes['streams'].append(stream_data)

            else:
                file_attributes['has_streams'] = False

    return file_attributes

def ffprobe_file(file):
    """check_output was introduced in python 2.7 so won't work for < 2.7.
        You can use Popen with communicate to get the output
        The file argument must be a full path to a file"""
    logger = logging.getLogger("media")

    if hardcoded_ffprobe_path is None:
        cmd = "which ffprobe"
        args = shlex.split(cmd)

        # We will use a different method to get ffprobe_path depending on python version
        if sys.version_info[0] == 2 and sys.version_info[1] == 7:
            ffprobe_path = subprocess.check_output(args).decode('utf-8')
        else:
            x = subprocess.Popen(args, stdout=subprocess.PIPE)
            ffprobe_path = x.communicate()[0].split()[0]
    else:
        ffprobe_path = hardcoded_ffprobe_path

    #cmd = ffprobe_path + ' "' + file.replace('"', r'\"') + '"' + " -v quiet -show_streams -show_format -print_format json"
    cmd = ffprobe_path + ' "' + file + '"' + " -v quiet -show_streams -show_format -print_format json"

    # /usr/local/bin/ffprobe '/Volumes/travolta/Expedat/1c_DigitalDelivery/strandreleasing/Daughter of Mine/Daughter of Mine Feature CLEAN ProRes.mov' -v quiet -show_streams -show_format -print_format json
    #args = shlex.split(cmd)    #original, worked great for ascii file names
    #args = shlex.split(unicode(cmd, "utf-8"))
    """The shlex.split() code wraps both unicode() and str() instances in a StringIO() object, which can only handle Latin-1 bytes (so not the full unicode codepoint range).
    You'll have to encode (to UTF-8 should work) if you still want to use shlex.split(); 
    """
    #print cmd # /usr/local/bin/ffprobe "/Users/john/temp/test/PKG - PKG - EUPHORIA-102_FRP_23/EUPHORIA-102_FRP_23_DIA_REC/Audio Files/EUPHORIA-102_FRP_23_DIA_REC_N°24.wav" -v quiet -show_streams -show_format -print_format json

    args = ushlex.split(cmd)

    # Log the command
    if debug is True:
        logger.debug('ffprobe cmd: {} {} -v quiet -show_streams -show_format -print_format json'.format(ffprobe_path, file))
    """
    output = subprocess.check_output(args).decode('utf-8')
    """
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if error:
        logger.error(error)
    return output

def view_ffprobe_output_as_dict(file):
    json_data = ffprobe_file(file)
    data = json.loads(json_data)
    pprint(data)
    return data