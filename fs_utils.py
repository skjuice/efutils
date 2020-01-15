# fileio.py

import os
from os import listdir
from os.path import isfile, join
import glob
import logging
import hashlib
import time
import random
import string
import fnmatch
import shutil
import json
from pathlib import Path
from pprint import pprint

logger = logging.getLogger(__name__)


def get_all_files_in_a_dir_without_recursing(path):
    onlyfiles = []
    try:
        onlyfiles = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    except OSError as e:
        logger.error("Error while fetching files", exc_info=True)

    return onlyfiles


def get_files_of_certain_extensions_in_a_dir(path, ext_list=[]):
    ''' Without recursion
        Example of list of extensions: ['scc', 'srt']
    '''
    files_grabbed = []
    for ext in ext_list:
        files_grabbed.extend(glob.glob(add_trailing_slash(path) + '*.' + ext))

    return files_grabbed


def add_trailing_slash(path):
    return os.path.join(path, '')


def listdir_nohidden(path):
    ''' Returns files and directories
        Excludes files starting with . (ie, hidden files)
        Returns generator object, so have to loop through'''
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def get_nonhidden_files_at_root_of_path(path):
    ''' Returns files only
        Excludes files starting with . (ie, hidden files)
        Returns generator object, so have to loop through'''
    for f in os.listdir(path):
        if not f.startswith('.') and isfile(join(path, f)):
            # yield f    #only returns filename
            yield join(path, f)


def listdir_nohidden_using_glob(path):
    """
    Non-recursive
    :param path:
    :return:
    """
    return glob.glob(os.path.join(path, '*'))


def get_directories_at_root_of_path(path, get_hidden=False):
    if get_hidden is False:
        return [join(path, name) for name in os.listdir(path) if
                os.path.isdir(os.path.join(path, name)) and not name.startswith('.')]

    # show_hidden is True
    return [join(path, name) for name in os.listdir(path) if
            os.path.isdir(os.path.join(path, name))]  # gets hidden directories


def testdir():
    dirs = get_subdirectories_at_root_of_path('/Users/john/Downloads/sample_audio_video_scc_files/scc', False)
    for dir in dirs:
        pass


def get_files_in_dir_recursively(path):
    """
    Gets all files recursively
    :param path:
    :return:
    """
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*'):
            matches.append(os.path.join(root, filename))

    return matches


def get_files_recursively_in_path(path):
    files = []
    p = Path(path)
    # for i in p.glob('**/*'):  #this works as well
    for i in p.rglob("*"):
        files.append(str(i))    # i is PosixPath object
        #print(i.name)   # DORA_AND_THE_CITY_OF_LOST_GOLD_20191030.xml
        #print(i)    # /Users/john/Downloads/temp/generatedXMLs/DORA_AND_THE_CITY_OF_LOST_GOLD_20191030.xml
    return files

def get_files_in_dir_recursively2(path, **kwargs):
    """
    fnmatch: module provides support for Unix shell-style wildcards, which are not the same as regular expressions
    *       matches everything
    ?       matches any single character
    [seq]   matches any character in sequence
    [!seq]  matches any character not in seq

    os.walk(top, topdown=True, onerror=None, followlinks=False)
    Generate the file names in a directory tree by walking the tree either top-down or bottom-up. For each directory
    in the tree rooted at directory top (including top itself), it yields a 3-tuple (dirpath, dirnames, filenames).

    dirpath is a string, the path to the directory. dirnames is a list of the names of the subdirectories in
    dirpath (excluding '.' and '..'). filenames is a list of the names of the non-directory files in dirpath.
    Note that the names in the lists contain no path components. To get a full path (which begins with top) to a
    file or directory in dirpath, do os.path.join(dirpath, name).


    :param path:
    :return:
    """
    matches = []
    for root, dirnames, filenames in os.walk(path):
        if 'skip_hidden_files' in kwargs:
            filenames = [f for f in filenames if not f[0] == '.']

        if 'skip_dirs' in kwargs:
            exclude_dirs = kwargs.get('skip_dirs').split(",")
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        if 'skip_hidden_dirs' in kwargs:
            dirnames[:] = [d for d in dirnames if not d[0] == '.']

        if 'allowed_extensions' in kwargs:
            patterns = ['*' + ext.strip() for ext in
                        kwargs.get('allowed_extensions').split(",")]  # produces pattern similar to get_patterns1()
        else:
            patterns = ['*']

        for filename in filenames:
            # print filename  #filename, including files in sub directories
            if any(fnmatch.fnmatch(filename.lower(), pattern) for pattern in patterns):
                # if files have uppercase extension, will still shove them in matches
                matches.append(os.path.join(root, filename))

    return matches


def get_patterns1():
    return [
        '*scc',
        '*log',
        '*txt'
    ]


def get_patterns2():
    return [
        '!*.scc'
    ]


def exclude_dirs():
    """
    When topdown is true, the caller can modify the dirnames list in-place (e.g., via del or slice assignment), and
    walk will only recurse into the subdirectories whose names remain in dirnames; this can be used to prune the search...

    dirs[:] = value modifies dirs in-place. It changes the contents of the list dirs without changing the container.
    As help(os.walk) mentions, this is needed if you wish to affect the way os.walk traverses the subdirectories.
    (dirs = value merely reassigns (or "binds") the variable dirs to a new list, without modifying the original dirs.)
    :return:
    """
    return [
        'subdirToIgnore'  # this needs to be the name of a subdirectory (at any level) to ignore
    ]
    # return []  #return empty list to not ignore any dir paths


def test():
    files = get_files_in_dir_recursively2('/Users/john/Downloads/sample_audio_video_scc_files')
    for file in files:
        pprint(file)


def path_is_a_dir_and_exists(path):
    return os.path.isdir(path)


def file_exists(file):
    return os.path.isfile(file)


def move_file(old_filepath, new_filepath):
    try:
        os.rename(old_filepath, new_filepath)
        return True
    except OSError:
        logger.error('File move failed as source file does not exist')
        return False


def find_file_in_path(file_name, path):
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return os.path.join(root, file_name)

    return None


def rename_file_with_prefix(file, prefix):
    """
    Do not throw any error, python will throw its own error if this fails. Just catch and handle in the calling function

    :param file: file must be a full path to a file
    :param prefix:
    :return:
    """
    old_filepath = file
    new_filepath = prefix_filename_with_string(file, prefix)
    rename_file(old_filepath, new_filepath)
    return new_filepath


def rename_file_with_suffix(file, suffix):
    """
    Do not throw any error, python will throw its own error if this fails. Just catch and handle in the calling function

    :param file: file must be a full path to a file
    :param suffix:
    :return:
    """
    old_filepath = file
    new_filepath = suffix_filename_with_string(file, suffix)
    rename_file(old_filepath, new_filepath)
    return new_filepath


def rename_file(old_filepath, new_filepath):
    """
    :param old_filepath:
    :param new_filepath: can be full path including new filename, or just the new filename
    :return:
    Do not throw any error, python will throw its own error if this fails. Just catch and handle in the calling function
    """
    if '/' in new_filepath:
        os.rename(old_filepath, new_filepath)
    else:
        containing_dir_path = get_containing_dir_from_full_file_path(old_filepath)
        new_filepath = containing_dir_path + '/' + new_filepath
        os.rename(old_filepath, new_filepath)


def prefix_filename_with_string(file, prefix):
    # file can be full path or just filename
    # /Volumes/Megatron/AnE/MoviePoster.jpg and MoviePoster.jpg both would work
    containing_dir, filename = os.path.split(file)
    return add_trailing_slash(containing_dir) + str(prefix) + '_' + filename


def suffix_filename_with_string(file, suffix):
    # file can be full path or just filename
    # /Volumes/Megatron/AnE/MoviePoster.jpg and MoviePoster.jpg both would work
    containing_dir, filename = os.path.split(file)
    parts = filename.rpartition('.')
    return add_trailing_slash(containing_dir) + parts[0] + '_' + suffix + '.' + parts[2]


def suffix_filename_with_unique_id(filename, suffix=None):
    # if '/' in filename:
    #     filename = get_filename_from_full_file_path(filename)
    # Above is not needed as it would work even if first argument was full path to file rather than just the filename
    # So /Volumes/Megatron/AnE/MoviePoster.jpg and MoviePoster.jpg both would work
    file_name_without_extension, file_extension = os.path.splitext(filename)
    if suffix is None:
        suffix = str(int(time.time()))
    return file_name_without_extension + '_' + suffix + file_extension


def move_file_to_destination(file, destination_dir, new_filename=None):
    """
    OSError will be raised if some error is encountered
    :param file:
    :param destination_dir:
    :param new_filename:
    :return:
    """
    if new_filename is None:
        current_filename = get_filename_from_full_file_path(file)
        new_path = add_trailing_slash(destination_dir) + current_filename
        os.rename(file, new_path)
    else:
        new_path = add_trailing_slash(destination_dir) + new_filename
        os.rename(file, new_path)

    return new_path


def move_dir_to_destination_dir(dir, destination_dir):
    shutil.move(dir, destination_dir)


def get_filename_from_full_file_path(filepath, return_type=None):
    """
    :param filepath: can be just the filename with extension or full file path
    :param return_type:
    :return:
    """
    base = os.path.basename(filepath)

    if return_type == 'filename_only':
        filename_without_ext = os.path.splitext(base)[0]
        return filename_without_ext
    elif return_type == 'extension_only':
        extension = os.path.splitext(base)[1]
        return extension.strip('.').lower()
    else:
        return base  # filename with extension


def get_containing_dir_from_full_file_path(filepath):
    containing_dir = os.path.abspath(os.path.join(filepath, os.pardir))
    return containing_dir


def md5(absolute_file_path):
    "Sometimes you won't be able to fit the whole file in memory. In that case, you'll have to read chunks of 4096 bytes sequentially and feed them to the Md5 function"
    hash_md5 = hashlib.md5()
    with open(absolute_file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def md5_2(absolute_file_path):
    "Sometimes you won't be able to fit the whole file in memory. In that case, you'll have to read chunks of 4096 bytes sequentially and feed them to the Md5 function"
    hash_md5 = hashlib.md5()
    with open(absolute_file_path, "r") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_category(file_extension):
    if file_extension in ('xls', 'xlsx', 'csv', 'txt', 'doc', 'pdf', 'odt'):
        return 'document'
    elif file_extension in ('jpg', 'jpeg', 'png', 'psd', 'bmp', 'lsr'):
        return 'artwork'
    elif file_extension in ('xml'):
        return 'metadata'
    elif file_extension in ('scc', 'itt', 'cap', 'srt', 'dfxp', 'ttml'):
        return 'captions'
    else:
        return 'general'


def get_file_extension(file):
    filename, file_extension = os.path.splitext(file)
    return file_extension[1:]


def is_json_file(file):
    return get_file_extension(file) == 'json'


def get_unique_timestamped_string():
    return str(int(time.time())) + random.choice(string.ascii_uppercase) + ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(5))


def convert_json_file_to_dictionary(file):
    '''
    Great for converting config.json to dict
    :param file:
    :return:
    '''
    config = None
    with open(file) as json_data_file:
        config = json.load(json_data_file)  # config is a dictionary now

    return config


def touch(path):
    # Create dir if does not exist
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    with open(path, 'a'):
        os.utime(path, None)


"""

john01-mac:~/Downloads/sample_audio_video_scc_files$ tree -ifpugDsa $PWD
/Users/john/Downloads/sample_audio_video_scc_files
[-rw-r--r-- john 1815495230        8196 Jun  6 04:01]  /Users/john/Downloads/sample_audio_video_scc_files/.DS_Store
[drwxr-xr-x john 1815495230          96 Jun  5 19:01]  /Users/john/Downloads/sample_audio_video_scc_files/movetohere
[-rwxr-xr-x john 1815495230      221407 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/movetohere/ASP41067_AETN-182360PAR_LFT_PBUY_SSR1-CONTENT_HD-ShowingRoots_-v201901061726.scc
[drwxr-xr-x john 1815495230         288 Jun 24 16:38]  /Users/john/Downloads/sample_audio_video_scc_files/scc
[drwxr-xr-x john 1815495230          96 Jun 24 16:38]  /Users/john/Downloads/sample_audio_video_scc_files/scc/.Trash
[-rw-r--r-- john 1815495230           0 Jun 24 16:38]  /Users/john/Downloads/sample_audio_video_scc_files/scc/.Trash/a_trashed_file.scc
[-rw-r--r-- john 1815495230      134857 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/scc/ASP33164_LMN_MOVE_172357_NLM_000_2398_120_20160202_00.mov.scc
[-rwxr-xr-x john 1815495230      141142 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41066_AETN-2391PAR_AHV_SPOP_S001-CONTENT-SpecialOpsMikeForce_-v201812042021.scc
[-rw-r--r-- john 1815495230      184562 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41843_LFT_MOVE_56085_HVG_000_5994_120_20161104_00.mov.scc
[-rw-r--r-- john 1815495230      198762 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41858_LFT_MFTM_54075_NLM_000_2997_120_20190418_4646MV_01.scc
[-rw-r--r-- john 1815495230           0 Jun 24 15:08]  /Users/john/Downloads/sample_audio_video_scc_files/scc/file_with_uppercase_extension.TXT
[drwxr-xr-x john 1815495230         224 Jun 24 15:21]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir
[-rw-r--r-- john 1815495230           0 Jun 24 15:02]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/.aHiddenTextFile.txt
[-rw-r--r-- john 1815495230           0 Jun 24 13:32]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/.hidden_file_in_subdir.log
[-rw-r--r-- john 1815495230      215472 Jun  5 18:42]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/ASP41861_LFT_MFTM_54999_NLM_000_2997_120_20190418_4643MV_01.scc
[drwxr-xr-x john 1815495230          96 Jun 24 15:21]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirNotToIgnore
[-rw-r--r-- john 1815495230           0 Jun 24 15:21]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirNotToIgnore/a_file_in_subdirNOTToIgnore.log
[drwxr-xr-x john 1815495230          96 Jun 24 15:20]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirToIgnore
[-rw-r--r-- john 1815495230           0 Jun 24 15:20]  /Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirToIgnore/a_file_in_subdirToIgnore.log


files = get_files_in_dir_recursively2('/Users/john/Downloads/sample_audio_video_scc_files',
                                      allowed_extensions='scc, txt',
                                      skip_dirs='subdirToIgnore',
                                      skip_hidden_files=True,
                                      skip_hidden_dirs=True)

Above gives the following files:

/Users/john/Downloads/sample_audio_video_scc_files/movetohere/ASP41067_AETN-182360PAR_LFT_PBUY_SSR1-CONTENT_HD-ShowingRoots_-v201901061726.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP33164_LMN_MOVE_172357_NLM_000_2398_120_20160202_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41066_AETN-2391PAR_AHV_SPOP_S001-CONTENT-SpecialOpsMikeForce_-v201812042021.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/file_with_uppercase_extension.TXT
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41843_LFT_MOVE_56085_HVG_000_5994_120_20161104_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41858_LFT_MFTM_54075_NLM_000_2997_120_20190418_4646MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/ASP41861_LFT_MFTM_54999_NLM_000_2997_120_20190418_4643MV_01.scc



files = get_files_in_dir_recursively2('/Users/john/Downloads/sample_audio_video_scc_files',
                                      allowed_extensions='scc, txt',
                                      skip_dirs='subdirToIgnore',
                                      skip_hidden_files=True)

Above gives the following files:

/Users/john/Downloads/sample_audio_video_scc_files/movetohere/ASP41067_AETN-182360PAR_LFT_PBUY_SSR1-CONTENT_HD-ShowingRoots_-v201901061726.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP33164_LMN_MOVE_172357_NLM_000_2398_120_20160202_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41066_AETN-2391PAR_AHV_SPOP_S001-CONTENT-SpecialOpsMikeForce_-v201812042021.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/file_with_uppercase_extension.TXT
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41843_LFT_MOVE_56085_HVG_000_5994_120_20161104_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41858_LFT_MFTM_54075_NLM_000_2997_120_20190418_4646MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/ASP41861_LFT_MFTM_54999_NLM_000_2997_120_20190418_4643MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/.Trash/a_trashed_file.scc


files = get_files_in_dir_recursively2('/Users/john/Downloads/sample_audio_video_scc_files',
                                      allowed_extensions='scc, txt',
                                      skip_dirs='subdirToIgnore')

Above gives the following files:

/Users/john/Downloads/sample_audio_video_scc_files/movetohere/ASP41067_AETN-182360PAR_LFT_PBUY_SSR1-CONTENT_HD-ShowingRoots_-v201901061726.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP33164_LMN_MOVE_172357_NLM_000_2398_120_20160202_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41066_AETN-2391PAR_AHV_SPOP_S001-CONTENT-SpecialOpsMikeForce_-v201812042021.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/file_with_uppercase_extension.TXT
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41843_LFT_MOVE_56085_HVG_000_5994_120_20161104_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41858_LFT_MFTM_54075_NLM_000_2997_120_20190418_4646MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/.aHiddenTextFile.txt
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/ASP41861_LFT_MFTM_54999_NLM_000_2997_120_20190418_4643MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/.Trash/a_trashed_file.scc



Above gives the following files:

files = get_files_in_dir_recursively2('/Users/john/Downloads/sample_audio_video_scc_files')

/Users/john/Downloads/sample_audio_video_scc_files/.DS_Store
/Users/john/Downloads/sample_audio_video_scc_files/movetohere/ASP41067_AETN-182360PAR_LFT_PBUY_SSR1-CONTENT_HD-ShowingRoots_-v201901061726.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP33164_LMN_MOVE_172357_NLM_000_2398_120_20160202_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41066_AETN-2391PAR_AHV_SPOP_S001-CONTENT-SpecialOpsMikeForce_-v201812042021.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/file_with_uppercase_extension.TXT
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41843_LFT_MOVE_56085_HVG_000_5994_120_20161104_00.mov.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/ASP41858_LFT_MFTM_54075_NLM_000_2997_120_20190418_4646MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/.hidden_file_in_subdir.log
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/.aHiddenTextFile.txt
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/ASP41861_LFT_MFTM_54999_NLM_000_2997_120_20190418_4643MV_01.scc
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirToIgnore/a_file_in_subdirToIgnore.log
/Users/john/Downloads/sample_audio_video_scc_files/scc/subdir/subdirNotToIgnore/a_file_in_subdirNOTToIgnore.log
/Users/john/Downloads/sample_audio_video_scc_files/scc/.Trash/a_trashed_file.scc



"""