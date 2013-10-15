#!/usr/bin/env python
'''
setup.py help for commands.

see distutils for additional information

Copyright (c) 2013 Paul Houghton <paul4hough@gmail.com>

'''
import subprocess as sp
import os
import sys
import platform as pl
from distutils.core import setup, Command

def try_command(cmd,expout=None):
    pout = None
    perr = None
    pstatus = -99
    try:
        print "PATH",os.environ['PATH']
        print "setup.py run:",' '.join(cmd)
        proc = sp.Popen(cmd, stdout=sp.PIPE,stderr=sp.PIPE)
        pout,perr = proc.communicate()
        pout = pout.decode('utf-8').strip()
        pstatus = proc.returncode
    except Exception,e:
        print repr(e)
        if pstatus == None:
            pstatus = -99
    finally:
        print pout+'\n'+perr

    if pstatus != 0:
        msg = "FAILED: {fs} - cmd: '{fc}'".format(fs=pstatus,
                                                  fc=' '.join(cmd))
        raise SystemExit(msg)

    if expout and expout not in pout:
        msg = "FAILED: {fs} - exp: '{fe}' in '{fo}".format(fs=pstatus,
                                                           fe=expout,
                                                           fo=pout)
        raise SystemExit(msg)


class test_unit(Command):
    description = "run automated unit tests"
    user_options = [
        ("to-run=", None, "list of tests to run (default all)"),
    ]

    def initialize_options(self):
        self.to_run = []

    def finalize_options(self):
        if self.to_run:
            self.to_run = self.to_run.split(",")

    def run(self):
        import tests

        count, failures = tests.unit(self.to_run)
        if failures:
            print("%d out of %d failed" % (failures, count))
            raise SystemExit("Test failures are listed above.")

class test_system(Command):

    description = 'run automated system test'
    user_options = [('NONE',None,"ugg none")]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print sp.check_output(['env'])
        try_command(['python',
                     'bin/install-puppet.py'])
        try_command(['puppet','--version'],'3.3')
        try_command(['puppet',
                     'apply',
                     '-e',
                     "notify { 'Hi from puppet' : }",])
        tsys = pl.system()
        (tosname,tosver,tosvname) = pl.dist()
        msg = 'PASS: System Test install puppet: {fs} {fo} {fv} {fvn}'
        print msg.format(fs=tsys,fo=tosname,fv=tosver,fvn=tosvname)

    def trun(self):
        print 'Big Fun'

        tstat = try_command(['sudo',
                             'python',
                             'bin/install-puppet.py'])
        if tstat != 0:
            print 'FAIL:',tstat
            sys.exit(tstat)

        #tstat, tout = try_command(['puppet','--version'])
        if '3.3' not in " 3.3 ":
            print 'Puppet install failed',tout
            raise SystemExit("Test failures are listed above.")


if __name__ == "__main__":

    cmd_classes = {
        "test_unit": test_unit,
        "test_system": test_system
    }

    setup(cmdclass=cmd_classes,
          name = 'install-puppet',
          packages = ['install-puppet'],
          version = "0.0.1",
          description = "puppet installer",
          author = "Paul Houghton",
          author_email = "paul4hough@gmail.com",
          url = "https://github.com/pahoughton/install-puppet/",
          keywords = ["puppet"],
          classifiers = [
             "Programming Language :: Python",
             "Programming Language :: Python :: 3",
             "Development Status :: 1 - Alpha",
             "Environment :: Other Environment",
             "Intended Audience :: System Administrators",
             "License :: OSI Approved :: Common Public Attribution License Version 1.0 (CPAL-1.0)",
             "Operating System :: RedHat, Debian, Darwin",
             "Topic :: System :: Installation/Setup",
             ],
          long_description = '''\
Implments instructions from pupplabs install web page as a python script.
        '''
    )
