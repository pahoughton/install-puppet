#/bin/bash
unset GEM_HOME
unset GEM_PATH
sudo python bin/install-puppet.py
puppet --version