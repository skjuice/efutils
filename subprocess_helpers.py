import subprocess

'''
subprocess.check_output() is a wrapper over subprocess.run(). 
It makes our lives easier by passing in some sensible defaults. 
One of those is making stdout=subprocess.PIPE. This directs the 
standard output of the command you are running back to your program. 
Similarly, you can direct the standard error output to your program 
by passing in argument, stderr=subprocess.PIPE, this will populate 
e.stderr where e is the exception.

By default, this function will return the data as encoded bytes. 
The actual encoding of the output data may depend on the command being 
invoked, so the decoding to text will often need to be handled at 
the application level.

    md5 = subprocess.check_output('which md5', shell=True)
    # b'/sbin/md5\n'
    
    md5.decode('utf-8').strip()
    '/sbin/md5'

This behaviour may be overridden by setting text, encoding, errors, 
or universal_newlines to True

    md5 = subprocess.check_output('which md5a', shell=True, text=True, stderr=subprocess.STDOUT)

try:
    out = subprocess.check_output(cmd, shell=True, universal_newlines=True)
except subprocess.CalledProcessError as e:
    exitcode, err = e.returncode, e.output


If check is true, and the process exits with a non-zero exit code, a CalledProcessError 
exception will be raised. Attributes of that exception hold the arguments, the exit code, 
and stdout and stderr if they were captured.
check_output() sets check=True behind the scenes

'''



def execute_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        # print(out.strip())  # strip \n
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        exitcode, err = e.returncode, e.output
        # print(exitcode)
        # print(err) #coming out as empty string
        return exitcode, err

def hash_file(file):
    exit_code, md5_binary_path = execute_cmd('which md5')
    if exit_code != 0:
        exit_code, md5_binary_path = execute_cmd('which md5sum')

    if exit_code == 0:
        exit_code, output = execute_cmd(f'{md5_binary_path} {file}')
        if exit_code == 0:
            # print(output)
            # md5sum gives output like so:
            #   3fd531a2f0c9693f5a559a831eb4f993  /Volumes/Megatron/__VS_Ingest/Ingest_Manual/ANE_TV_5692_ASP27972_StorageWars_AEID75291_CC.scc
            # md5 on mac gives output like so:
            #   MD5 (/Users/sharadku/Downloads/temp/meta-PMRS1354250-818509-VOD_1_1_HAPL_1574457166.xml) = 8d8b26d9107127e00a776e5c36beb3df
            if '=' in output:
                return output.rpartition('=')[2].strip()
            else:
                return output.partition(' ')[0].strip()
