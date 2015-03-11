# a duct-tape-and-bubble-gum version of foreman's env support
import os
import subprocess

def run_in_env(command, filename='.env'):
    # configure environment as a copy of the current environment
    env = {}
    env.update(os.environ)
    # plus vars from the file
    with open(filename, 'r') as config:
        for line in config.readlines():
            # ignore whitespace padding
            line.strip()
            tmp = line.split('=')
            # further ignore whitespace padding that was around the =
            tmp = map(str.strip, tmp)
            if len(tmp[0]) and tmp[0][0] == '#':
                pass
            # check for nonempty variable and content
            elif len(tmp) == 2 and len(tmp[0]) and len(tmp[1]):
                env[tmp[0]] = tmp[1].strip("'") # drop quotes around values
    # run command
    subprocess.check_call(command, env=env)
    # check_call fires an exception on failure.
    # if we're here, both calls succeeded.
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(run_in_env(sys.argv[1:], '.env'))
