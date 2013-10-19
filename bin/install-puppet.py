#!/usr/bin/env python
'''install-puppet.py

install puppet on Darwin (OS X), RedHat and Debian systems.

ping travis
'''
import os
import sys
import platform
import urllib
import subprocess as sp
import re
import tempfile

def which(filename):
    """return the full path to an executable"""
    locs = os.environ.get("PATH").split(os.pathsep)
    for loc in locs:
        fn = os.path.join(loc, filename)
        if os.path.isfile(fn) and os.access(fn, os.X_OK):
            #print 'found:',fn
            return fn
    return None

def real_sysdo(cmd,expout=None,shell=False):
    '''real_sysdo - execute cmd and show output
    '''
    pcmd = None
    pout = None
    perr = None
    pstatus = -99
    if shell:
        pcmd = ' '.join(cmd)
    else:
        pcmd = cmd
        
    try:
        print "PATH",os.environ['PATH']
        print "run:",'~'.join(pcmd)
        proc = sp.Popen(pcmd, stdout=sp.PIPE,stderr=sp.PIPE,shell=shell)
        pout,perr = proc.communicate()
        pstatus = proc.returncode
        
    except Exception,e:
        print repr(e)
        if pstatus == None:
            pstatus = -99
    finally:
        if pout:
            print "STDOUT:"
            sys.stdout.write(pout)
        if perr:
            print "STDERR:"
            sys.stdout.write(perr)
        if not pout and not perr:
            print '-- NO OUTPUT --'
            
    if pstatus != 0:
        msg = "FAILED: {fs} - cmd: '{fc}'".format(fs=pstatus,
                                                  fc=' '.join(cmd))
        raise Exception(msg)

    if expout and expout not in pout:
        msg = "FAILED: {fs} - exp: '{fe}' in '{fo}".format(fs=pstatus,
                                                           fe=expout,
                                                           fo=pout)
        raise Exception(msg)

def unit_test_sysdo(cmd):
    print 'UT:',cmd
    return cmd

def install_osx_package(pkgfn):
    '''install an osx .pkg file
    '''
    instcmd = ['installer',
               '-verbose',
               '-dumplog',
               '-pkg',
               pkgfn,
               '-target',
               '/']
    print 'install:',' '.join(instcmd)
    sout = None
    installed = False
    try:
        sout = sysdo(instcmd)
        print sout
        installed = True
    except Exception,e:
        print 'FAILED',e
        if sout:
            print sout

    return installed

def install_puppet(sysname,osname=None,osver=None,osvername=None):
    '''install puppet

    returns true on success, false on failure
    '''
    print 'Installing puppet'
    if sysname == 'Darwin':
        tmpdir = 'build/tmp'
        mntdir = os.path.join(tmpdir,'mount')

        if not os.path.isdir(mntdir):
            os.makedirs(mntdir)

        url_base = 'http://downloads.puppetlabs.com/mac/'
        files = ['puppet-3.3.0.dmg',
                 'facter-1.7.3.dmg',
                 'hiera-1.2.1.dmg']

        for fn in files:
            dmgfn = os.path.join(tmpdir,fn)
            pkgfn = os.path.join(mntdir,fn.replace('.dmg','.pkg'))

            if not os.path.isfile(dmgfn):
                urllib.urlretrieve(url_base+fn,
                                   os.path.join(tmpdir,fn))

            mntcmd = ['hdiutil',
                      'attach',
                      '-mountpoint',
                      mntdir,
                      os.path.join(tmpdir,fn)]
            sysdo(mntcmd)

            didinstall = install_osx_package(pkgfn)
            umntcmd = ['hdiutil',
                       'detach',
                       mntdir]
            sysdo(umntcmd)
            if not didinstall:
                print 'FAILED - install puppet'
                sys.exit(1)

        # clean out any existing macports and reinstall
        try:
            sysdo(['/opt/local/bin/port','-fp','uninstall'])
        except Exception, e:
            print 'No ports found'

        try:
            print 'Clean old macports'
            sysdo(['rm','-rf',
                   '/opt/local',
                   '/Applications/DarwinPorts',
                   '/Applications/MacPorts',
                   '/Library/LaunchDaemons/org.macports.*',
                   '/Library/Receipts/DarwinPorts*.pkg',
                   '/Library/Receipts/MacPorts*.pkg',
                   '/Library/StartupItems/DarwinPortsStartup',
                   '/Library/Tcl/darwinports1.0',
                   '/Library/Tcl/macports1.0',
                   '~/.macports'],
                  shell=True)
        except Exception, e:
            raise e

        mport_pkg_fn = os.path.join(tmpdir,'MacPorts-2.2.0.pkg')
        urllib.urlretrieve('https://distfiles.macports.org/MacPorts/MacPorts-2.2.0-10.8-MountainLion.pkg',
                           mport_pkg_fn)

        if not install_osx_package(mport_pkg_fn):
            raise Exception('Install macports failed')

        sysdo(['/opt/local/bin/port','-v','selfupdate'])
        
    elif sysname == 'Linux':
        yum_platforms = ['fedora','centos','redhat']
        if osname in yum_platforms:
            repourl = 'http://yum.puppetlabs.com/'
            repoloc = None
            if osname in ['centos','redhat']:
                repoloc = '/'.join(['el',
                                   osver,
                                   'products',
                                   'i386',
                                   'puppetlabs-release-'
                                   +osver
                                   +'-7.noarch.rpm'])
            elif osname == 'fedora':
                repoloc = '/'.join(['fedora',
                                    'f'+osver,
                                    'products',
                                    'i386',
                                    'puppetlabs-release-'])
                if osver in ['17','18']:
                    repoloc += osver + '-7'
                elif osver == '19':
                    repoloc += osver + '-2'
                else:
                    print 'Unsupported OS:',osname,' ',osver
                    sys.exit(1)
                repoloc +='.noarch.rpm'
            else:
                print 'Unsupported OS:',os_name,' ',os_ver
                sys.exit(1)

            sysdo(['rpm', '-ivh', repourl+repoloc])
            sysdo(['yum', '-y','install', 'puppet'])

        elif osname in ['Ubuntu','debian']:
            fname = 'puppetlabs-release-'+osvername+'.deb'
            url = 'http://apt.puppetlabs.com/'

            sysdo(['wget', url+fname])
            sysdo(['dpkg','-i',fname])
            sysdo(['apt-get','-y','update'])
            sysdo(['apt-get','-y','install','puppet'])

        else:
            print 'Unsupported platform:',sysname,osname
            sys.exit( 1 )

    else:
        print 'Unsupported platform:',sysname
        sys.exit( 1 )

    for k,v in os.environ.iteritems():
        print '{fk}={fv}'.format( fk=k,fv=v)
        
    # Travis needs gems installed with bundle
    # AND does NOT set the TRAVIS environment variable when
    # sudo is used :( - hack workarounds
    if os.path.isfile( os.environ['HOME']+'/.travis_ci_environment.yml' ):
        # travis-ci requires the bundle gem install of puppet
        # because of the users environment. Otherwise the
        # the puppet command will fail.
        bndl_cmd = None
        gemfile = tempfile.NamedTemporaryFile(mode='w',delete=False)
        if os.getuid() == 0:
            # need to install as normal user
            if os.environ.get('SUDO_USER'):
                bndl_cmd = ['su','-',os.environ['SUDO_USER'],'-c',
                            'bundle install --gemfile='+gemfile.name]
            else:
                gemfile.close()
                os.remove(gemfile.name)
                raise Exception('SUDO_USER not set, need non root user id')
        else:
            bndl_cmd = ['bundle install --gemfile='+gemfile.name]
        
        gemfile.write("source 'https://rubygems.org'\ngem 'puppet'\n")
        gemfile.close()
        os.chmod(gemfile.name, 0664)
        sysdo(['ls','-l',gemfile.name])
        sysdo(bndl_cmd)
        os.remove(gemfile.name)
#         wasdir = os.getcwd()
#         os.chdir(os.path.dirname(sys.argv[0]))
#         if re.match(r'/bin$', os.getcwd()):
#             os.chdir(re.sub( r'(.*)/bin','\1',os.getcwd() ))
#         else:
#             # hope for the best
#             os.chdir('..')
#         print 'CWD:',os.getcwd()
#         gemfile = open('Gemfile','w')
#         gemfile.write("source 'https://rubygems.org'\ngem 'puppet'\n")
#         gemfile.close()
#         sysdo(['cat','Gemfile'])
#         sysdo(['bundle','list'])
#         os.chdir(wasdir)
#         sysdo(['cat',gemfile.name])
        sysdo(['gem','install','puppet'])
        
        print 'puppet gem installed for travis.'

def main():
    '''main - script entry point'''
    global sysdo
    sysname = None
    osname = None
    osver = None
    osvername = None
    if os.environ.get('script_unit_test'):
        print 'Running Unit Test:',os.environ['script_unit_test']
        sysdo = unit_test_sysdo
        test_os = os.environ['script_unit_test']
        test_os_info = test_os.split(' ')
        sysname = test_os_info[0]
        if len(test_os_info) > 1:
            osname = test_os_info[1]
        if len(test_os_info) > 2:
            osver = test_os_info[2]
        if len(test_os_info) > 3:
            osvername = test_os_info[3]
        install_puppet(sysname,osname,osver,osvername)
    else:
        sysdo = real_sysdo
        sysname = platform.system()
        (osname,osver,osvername) = platform.dist() 
        
        if which('puppet'):
            sout = sp.check_output(['puppet','--version']).decode('utf-8')
            if '3.3' in sout:
                print 'Puppet 3.3 found'
            else:
                install_puppet(sysname,osname,osver,osvername)
        else:
            install_puppet(sysname,osname,osver,osvername)
        
    print( 'Puppet installed as ',which('puppet'),'enjoy ;)')

if __name__ == '__main__':
    main()
    
