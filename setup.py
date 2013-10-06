import subprocess as sp
import sys
from distutils.core import setup, Command


class test_unit(Command):
    description = "run automated tests"
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
    
    def run(self):
        print sp.check_output(['python',
                               'bin/install-puppet.py']
                              ).decode('utf-8').strip()
        vout = sp.check_output(['puppet','--version'])
        if '3.3' not in vout:
            print 'Puppet install failed',vout
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
