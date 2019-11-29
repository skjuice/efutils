# utils.py
from os.path import basename,splitext

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    #__getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__


def is_ascii(text):
    if isinstance(text, unicode):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    else:
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    return True

def sort_files_list_alphabetically(files, include_file_extension_in_sorting=False):
    """
    Running into issues sorting list of filepaths because of unicode characters in filenames
    Strategy is to separate filepaths into two lists - one for filepaths that only contain ascii
    and another for filepaths that contain unicode chars.
    Then sort the ascii only list
    Later merge the two list and return that

    :param files:
    :return:
    """
    ascii_filepaths = []
    unicode_filepaths = []

    for file in files:
        #print type(file)
        if is_ascii(file):
            # file contains only ASCII chars
            ascii_filepaths.append(file)
        else:
            # file contains unicode chars
            unicode_filepaths.append(file)

    #files = [str(x) for x in files] #don't need to convert list of unicodes to list of strings for sorting to work


    # new_list = [splitext(basename(x))[0] for x in ascii_filepaths]
    # if ascii_filepaths was:   ['/home/john/test 1.jpg','/home/john/some_movie_file_with_subs.mov','/home/john/archive.zip']
    # new_list would be:        ['test 1', 'some_movie_file_with_subs', 'archive']
    # splitext(basename('/home/john/sub dir/hello1_asfd.mxf')) GIVES: ('hello1_asfd', '.mxf')

    if include_file_extension_in_sorting is True:
        new_list = [basename(x) for x in ascii_filepaths]
    else:
        new_list = [splitext(basename(x))[0] for x in ascii_filepaths]

    fin_list = list(zip(ascii_filepaths, new_list)) #gives a list of tuples. Each tuple, x[0] is full filepath and x[1] is just the filename without extension
    sorted_ascii_list = [x[0] for x in sorted(fin_list, key=lambda x: x[1])]

    return sorted_ascii_list + unicode_filepaths

def convert_dict_to_dotdict(myDict):
    return DotDict(myDict)