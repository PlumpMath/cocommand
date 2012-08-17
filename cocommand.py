#!/usr/bin/env python
'''
run more command use gevent coroutine
author: smallfish <smallfish.xy@gmail.com>
usage:
    ./cocommand.py -f [FILE] -c [CONCURRENT] -t [TIMEOUT]'
'''
from __future__ import with_statement
from sys import exit
from optparse import OptionParser
try:
    import gevent
    import gevent.subprocess as subprocess
except:
    print 'require gevent'
    exit(1)

# errors output
errors = []

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
    code, out, err = 0, '', ''
    with gevent.Timeout(opts.timeout, False):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        code = p.returncode
        if code == 0:
            return cmd, True
        else:
            errors.append({"command": cmd, "code": code, "error": err, "out": out})
            return cmd, False
    code = -1
    err  = 'timeout>%d' % opts.timeout
    errors.append({"command": cmd, "code": code, "error": err, "out": out})
    return cmd, False

def array_split(array, n):
    result = []
    m = len(array)
    count = m/n
    if m % n != 0:
        count += 1
    for i in xrange(count):
        start, end = i*n, (i+1)*n
        result.append(array[start:end])
    return result

def get_file_lines(f):
    return [line.strip() for line in open(f) if line]

def main():
    for group in array_split(get_file_lines(opts.file), opts.concurrency):
        for (cmd, result) in spawn_jobs(group, spawn_command):
            print '%s\t%s' % (cmd, result and 'SUCCESS' or 'FAILURE') 
    if errors:
        f = 'cocommand_errors.log'
        open(f, 'w').writelines('\n'.join([str(item) for item in errors]))
        print 'write errors into %s, line: %d' % (f, len(errors))

if __name__ == '__main__':
    main()
