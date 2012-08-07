#!/usr/bin/env python
'''
run more command use gevent coroutine
author: smallfish <smallfish.xy@gmail.com
usage:
    ./cocommand.py -f [FILE] -c [CONCURRENT] -t [TIMEOUT]'
'''
from sys import exit
from optparse import OptionParser
from itertools import izip_longest
try:
    import gevent
    import gevent.subprocess as subprocess
except:
    print 'require gevent'
    exit(1)

parser = OptionParser(usage='%prog -f [FILE] -c [CONCURRENT] -t [TIMEOUT]')
parser.add_option('-f', '--file', metavar='filename', help='file with command list')
parser.add_option('-c', '--concurrency', default=10, type='int', metavar='num', help='concurrency num, default: %default')
parser.add_option('-t', '--timeout', default=3, type='int', metavar='num', help='execute timeout, default: %default')
(opts, args) = parser.parse_args()

if not opts.file:
    parser.print_help()
    exit(2)

def spawn_jobs(group, func):
    jobs = [gevent.spawn(func, item) for item in group if item]
    gevent.joinall(jobs)
    return [job.value for job in jobs]

def spawn_command(cmd):
    with gevent.Timeout(opts.timeout, False):
        ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ret == 0:
            return cmd, True
    return cmd, False

def array_split(array, n):
    args = [iter(array)] * n
    return list(izip_longest(*args))

def get_file_lines(f):
    return [line.strip() for line in open(f) if line]

def main():
    for group in array_split(get_file_lines(opts.file), opts.concurrency):
        for (cmd, result) in spawn_jobs(group, spawn_command):
            print '%s\t%s' % (cmd, result and 'SUCCESS' or 'FAILURE') 

if __name__ == '__main__':
    main()
