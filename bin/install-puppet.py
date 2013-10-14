#!/usr/bin/env python
'''install-puppet.py - install puppet

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

def real_sysdo(cmd):
    print 'run:',' '.join(cmd)
    sout = sp.check_output(cmd).decode('utf-8')
    print repr(sout)

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
                sys.exit(1)

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

    # Travis needs gems installed with bundle
    if os.environ.get('TRAVIS'):
        # gemfile = tempfile.NamedTemporaryFile(mode='w',delete=False)
        # gemfile.write( "gem 'puppet'\n")
        # gemfile.close()
        wasdir = os.getcwd()
        mydir = os.path.dirname(sys.argv[0])
        if '/bin' in mydir:
            mydir = mydir.replace('/bin','')
            print 'MYDIR:',mydir

        os.chdir(mydir)
        print 'CWD:',os.getcwd()
        sysdo(['cat','Gemfile'])
        sysdo(['bundle','install'])
        os.chdir(wasdir)
        print 'puppet gem installed.'

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
    
