# export a foreman env to heroku
import subprocess

def export_env(filename='.env'):
    data=['heroku', 'config:set']
    unset=['heroku', 'config:unset']
    with open(filename, 'r') as config:
        for line in config.readlines():
            # ignore whitespace padding
            line.strip()
            tmp = line.split('=')
            # further ignore whitespace padding that was around the =
            tmp = map(str.strip, tmp)
            # Strip any quotes that might show up around the string
            def striphyphen(somestring):
                return somestring.strip("'").strip('"')
            tmp = map(striphyphen, tmp)
            if len(tmp[0]) and tmp[0][0] == '#':
                # the heroku CLI cannot return if a variable is not yet set
                # or if it has been set to the empty string.
                # delete commented-out variables to be safe.
                unset.append(tmp[0][1:])
            # check for nonempty variable and content
            elif len(tmp) == 2 and len(tmp[0]) and len(tmp[1]):
                    
                data.append('{0}={1}'.format(*tmp))
    # run heroku configuration
    subprocess.check_call(data)
    subprocess.check_call(unset)
    # check_call fires an exception on failure.
    # if we're here, both calls succeeded.
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(export_env('.env'))
