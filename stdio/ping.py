import sys
import time

print('utc({}) time({}) argv({})'.format(
    int(time.time()), time.strftime('%c'), ' '.join(sys.argv)))
