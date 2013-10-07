#/bin/bash
unset GEM_HOME
unset GEM_PATH
PATH=/opt/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin
sudo python bin/install-puppet.py
head /usr/bin/puppet
puppet --version