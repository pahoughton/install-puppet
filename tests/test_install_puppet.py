import os
import subprocess as sp

from tests import TestCase, add

class TestInstallPuppet(TestCase):

    script_fn = 'bin/install-puppet.py'
    
    osexp = {'Darwin 12' : 
             ['Running Unit Test: Darwin 12',
              'Installing puppet',
              "UT: ['hdiutil', 'attach', '-mountpoint', 'build/tmp/mount', 'build/tmp/puppet-3.3.0.dmg']",
              "install: installer -verbose -dumplog -pkg build/tmp/mount/puppet-3.3.0.pkg -target /",
              "UT: ['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/puppet-3.3.0.pkg', '-target', '/']",
              "['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/puppet-3.3.0.pkg', '-target', '/']",
              "UT: ['hdiutil', 'detach', 'build/tmp/mount']",
              "UT: ['hdiutil', 'attach', '-mountpoint', 'build/tmp/mount', 'build/tmp/facter-1.7.3.dmg']",
              "install: installer -verbose -dumplog -pkg build/tmp/mount/facter-1.7.3.pkg -target /",
              "UT: ['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/facter-1.7.3.pkg', '-target', '/']",
              "['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/facter-1.7.3.pkg', '-target', '/']",
              "UT: ['hdiutil', 'detach', 'build/tmp/mount']",
              "UT: ['hdiutil', 'attach', '-mountpoint', 'build/tmp/mount', 'build/tmp/hiera-1.2.1.dmg']",
              "install: installer -verbose -dumplog -pkg build/tmp/mount/hiera-1.2.1.pkg -target /",
              "UT: ['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/hiera-1.2.1.pkg', '-target', '/']",
              "['installer', '-verbose', '-dumplog', '-pkg', 'build/tmp/mount/hiera-1.2.1.pkg', '-target', '/']",
              "UT: ['hdiutil', 'detach', 'build/tmp/mount']",
              ],
             'Linux fedora 19' :
             ['Running Unit Test: Linux fedora 19',
              'Installing puppet',
              "UT: ['rpm', '-ivh', 'http://yum.puppetlabs.com/fedora/f19/products/i386/puppetlabs-release-19-2.noarch.rpm']",
              "UT: ['yum', '-y', 'install', 'puppet']",
              ],
             'Linux fedora 18' :
             ['Running Unit Test: Linux fedora 18',
              'Installing puppet',
              "UT: ['rpm', '-ivh', 'http://yum.puppetlabs.com/fedora/f18/products/i386/puppetlabs-release-18-7.noarch.rpm']",
              "UT: ['yum', '-y', 'install', 'puppet']",
              ],
             'Linux fedora 17' :
             ['Running Unit Test: Linux fedora 17',
              'Installing puppet',
              "UT: ['rpm', '-ivh', 'http://yum.puppetlabs.com/fedora/f17/products/i386/puppetlabs-release-17-7.noarch.rpm']",
              "UT: ['yum', '-y', 'install', 'puppet']",
              ],
             'Linux Ubuntu 13.04 raring' :
             ['Running Unit Test: Linux Ubuntu 13.04 raring',
              'Installing puppet',
              "UT: ['wget', 'http://apt.puppetlabs.com/puppetlabs-release-raring.deb']",
              "UT: ['dpkg', '-i', 'puppetlabs-release-raring.deb']",
              "UT: ['apt-get', '-y', 'update']",
              "UT: ['apt-get', '-y', 'install', 'puppet']",
              ],
             'Linux Ubuntu 12.10 quantal' :
             ['Running Unit Test: Linux Ubuntu 12.10 quantal',
              'Installing puppet',
              "UT: ['wget', 'http://apt.puppetlabs.com/puppetlabs-release-quantal.deb']",
              "UT: ['dpkg', '-i', 'puppetlabs-release-quantal.deb']",
              "UT: ['apt-get', '-y', 'update']",
              "UT: ['apt-get', '-y', 'install', 'puppet']",
              ],
             'Linux debian 7 wheezy' :
             ['Running Unit Test: Linux debian 7 wheezy',
              'Installing puppet',
              "UT: ['wget', 'http://apt.puppetlabs.com/puppetlabs-release-wheezy.deb']",
              "UT: ['dpkg', '-i', 'puppetlabs-release-wheezy.deb']",
              "UT: ['apt-get', '-y', 'update']",
              "UT: ['apt-get', '-y', 'install', 'puppet']",
              ],
             'Linux debian 6 squeeze' :
             ['Running Unit Test: Linux debian 6 squeeze',
              'Installing puppet',
              "UT: ['wget', 'http://apt.puppetlabs.com/puppetlabs-release-squeeze.deb']",
              "UT: ['dpkg', '-i', 'puppetlabs-release-squeeze.deb']",
              "UT: ['apt-get', '-y', 'update']",
              "UT: ['apt-get', '-y', 'install', 'puppet']",
              ],
             } 
       
    def run_script(self,test_os):
        '''run the script in test mode.
        '''
        tenv = os.environ
        tenv['script_unit_test'] = test_os
        proc = sp.Popen(['python',self.script_fn],
                      stdin=sp.PIPE,
                      stdout=sp.PIPE,
                      stderr=sp.STDOUT,
                      env=tenv)        
        (scriptOut,scriptErr) = proc.communicate()
        scriptOutStr = scriptOut.decode('utf-8').strip()
        if scriptErr:
            scriptOutStr += scriptErr.decode('utf-8').strip()
        return scriptOutStr
    
    def verify_script_output(self, sout, explines):
        '''compare script output to expected lines
        '''
        lnum = 0
        for lval in sout.split('\n'):
            if lnum < len(explines):
                self.assertEqual(lval,explines[lnum])
                lnum += 1
            else:
                break
            
    def test_script(self):
        '''verify output for each os being tested'''
        print
        for osid in self.osexp:
            self.verify_script_output(self.run_script(osid), 
                                      self.osexp[osid])
            print osid,"unit tested."

add(TestInstallPuppet)
    