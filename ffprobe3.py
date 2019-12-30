# -*- coding: utf-8 -*-
# above is to fix the error syntaxError: Non-ASCII character '\xc2' in file audit.py on line n

import os
import fs_utils
import sys
import subprocess
import logging
import shlex
#import ushlex
import json
from pprint import pprint
import locale

suffix = None
ffprobe_suitable_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".mov", ".mp4", ".ts", ".mpg", ".mpeg", ".mkv", ".mxf", ".wav", ".avi", ".mp2", ".mp3", ".scc", ".srt", ".stl"]
hardcoded_ffprobe_path = None
max_file_size_for_checksum = 1 #in GB
debug = True
logger = logging.getLogger("media")


def get_ffprobe_binary_location():
    try:
        result = subprocess.check_output(["which", "ffprobe"])
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        pprint(e)
        return False


# for python3, no encoding/decoding bullshit
def gather_media_info(file, hash=False):
    """file argument needs to be the absolute path to a file"""
    #pprint(type(file))  # <class 'str'>

    file_attributes = {}
    duration = None
    frame_rate = None
    audio_channel_count = 0
    audio_track_count = 0
    filename, file_extension = os.path.splitext(file)

    #Skip hidden files. This logic should be put into get_files method. basename will give the filename with extension only
    if os.path.basename(file).startswith('.'):
        return file_attributes

    file_attributes['file_path'] = file
    file_attributes['file_name'] = os.path.basename(file) #filename with extension
    file_attributes['containing_dir'] = os.path.dirname(file)
    file_attributes['file_extension'] = file_extension[1:].lower()  #if file_extension was '.scc', then this would give 'scc'
    file_attributes['file_size'] = os.path.getsize(file)
    file_attributes['ffprobed'] = False

    # If file size is less than the defined size for running checksum on, then hash it
    if shouldHashBasedOnFileSize(file):
        file_attributes['md5'] = fileio.md5(file)
    else:
        if hash is True:
            file_attributes['md5'] = fileio.md5(file)
        else:
            file_attributes['md5'] = None

    if file_extension.lower() in ffprobe_suitable_extensions:
        file_attributes['ffprobed'] = True

        # file is suitable for ffprobe
        #json_data = ffprobe_file(file)
        #data = json.loads(json_data)    #data is a dictionary

        # for python 3:
        data = ffprobe_file(file)  #data is a dictionary

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
                    stream_data['codec_type']           = stream.get('codec_type')  #if codec_type doesn't exist, the name on LHS will store None
                    stream_data['codec_name']           = stream.get('codec_name')
                    stream_data['codec_long_name']      = stream.get('codec_long_name')
                    stream_data['codec_tag']            = stream.get('codec_tag')
                    stream_data['codec_tag_string']     = stream.get('codec_tag_string')
                    stream_data['codec_time_base']      = stream.get('codec_time_base')

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

    #pprint(file_attributes)
    #pprint('file attributes above')
    return file_attributes

def ffprobe_file(file):
    '''
    Built for python 3
    :param file:
    :return:
    '''
    ffprobe_path = get_ffprobe_binary_location()
    #file = '/Users/john/media_files/Sample Videos _ Dummy Videos For Demo Use-EngW7tLk6R8.mkv'
    # When passing filepath to shell, should probably do this: file.encode(locale.getpreferredencoding()) ??
    # file would be a Str object in python3

    if ffprobe_path:
        #cmd = ffprobe_path + ' "' + file + '"' + " -v quiet -show_streams -show_format -print_format json"

        # this below gives this error: TypeError: can only concatenate str (not "bytes") to str
        #cmd = ffprobe_path + ' "' + file.encode(locale.getpreferredencoding()) + '"' + " -v quiet -show_streams -show_format -print_format json"



        #result = subprocess.run([ffprobe_path, file, '-v', 'quiet', '-show_streams', '-show_format', '-print_format', 'json'], stdout=subprocess.PIPE)

        # with below, we get this error if filename is as such:
        # /Users/john/media_files/audio/Euphoria 101 Fr Dubs/Test_eup_001_797366_french_51_rs_23984\udcc2\udcb0C_DNU.wav
        # UnicodeEncodeError: 'utf-8' codec can't encode characters in position 93-94: surrogates not allowed
        #result = subprocess.run(
        #    [ffprobe_path, file.encode(locale.getpreferredencoding()), '-v', 'quiet', '-show_streams', '-show_format', '-print_format', 'json'],
        #    stdout=subprocess.PIPE)

        # with below, we no longer get this error: UnicodeEncodeError: 'utf-8' codec can't encode characters in position 93-94: surrogates not allowed
        result = subprocess.run(
                [ffprobe_path, file.encode('utf8','surrogateescape'), '-v', 'quiet', '-show_streams', '-show_format', '-print_format', 'json'],
                stdout=subprocess.PIPE)

        output = result.stdout.decode('utf-8')
        #pprint(output)
        #pprint(json.loads(output))
        return json.loads(output) # a dictionary

    else:
        return None

def bytesto(bytes, to, bsize=1024):
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesto(314575262000000, 'm')))

       sample output:
           mb= 300002347.946
    """
    a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
    r = float(bytes)
    for i in range(a[to]):
        r = r / bsize

    return(r)

def shouldHashBasedOnFileSize(file):
    if bytesto(os.path.getsize(file), 'g') <= max_file_size_for_checksum:
        return True
    else:
        return False