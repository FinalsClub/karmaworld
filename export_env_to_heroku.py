import subprocess

def export_env(filename='.env'):
    data=['heroku', 'config:set']
    with open(filename, 'r') as config:
        for line in config.readlines():
            # ignore whitespace padding
            line.strip()
            tmp = line.split('=')
            # further ignore whitespace padding that was around the =
            tmp = map(str.strip, tmp)
            # check for nonempty variable and content
            if len(tmp) == 2 and len(tmp[0]) and len(tmp[1]):
                data.append('{0}={1}'.format(*tmp))
    return subprocess.check_call(data)

if __name__ == '__main__':
    import sys
    sys.exit(export_env('.env.example'))
