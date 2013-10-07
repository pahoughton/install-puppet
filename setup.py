import subprocess as sp
import os
import sys
import platform as pl
from distutils.core import setup, Command

os.environ['PATH'] = '/opt/local/bin:/usr/bin:/bin'
del os.environ['GEM_HOME']
del os.environ['GEM_PATH']


def try_command(cmd):
    cout = None
    cerr = None
    cstatus = -99
    try:
        print "run:",' '.join(cmd)
        proc = sp.Popen(cmd, stdout=sp.PIPE,stderr=sp.PIPE
                        ).decode('utf-8').strip()
        cout,cerr = proc.communicate()
        cstatus = proc.returncode
    except Exception,e:
        print repr(e)
        if cstatus == None:
            cstatus = -99
    finally:
        print repr(cout)+'\n'+repr(cerr)
        if cstatus != 0:
            print 'FAILED:',cstatus
    
    return cstatus, cout, cerr

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
        tstat = try_command(['sudo',
                             'python',
                             'bin/install-puppet.py'])
        if tstat != 0:
            sys.exit(tstat)
        tstat, tout = try_command(['puppet','--version'])
        
        if '3.3' not in tout:
            print 'Puppet install failed',tout
            raise SystemExit("Test failures are listed above.")
        
        tstat, tout = try_command(['puppet',
                                   'apply',
                                   '-e',
                                   "notify { 'Hi from puppet' : }",])
        if tstat != 0:
            sys.exit(tstat)
        else: 
            tsys = pl.system()
            (tosname,tosver,tosvname) = pl.dist()
            msg = 'PASS: System Test install puppet: {fs} {fo) {fv} {fvn}'
            print msg.format(fs=tsys,fo=tosname,fv=tosver,fvn=tosvname)
            
            
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
