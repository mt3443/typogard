# Generates npm_transitive_results, shows potential typosquatting targets for all packages and their transitive dependencies

import typosquatting
import sys
import os

node_name = sys.argv[1]

os.system('rm -rf /dev/shm/npm')
os.system('mkdir /dev/shm/npm')
typosquatting.scan_all('cluster_input/{}'.format(node_name), '/dev/shm/npm/transitive_output')
os.system('cat /dev/shm/npm/transitive_output >> /volatile/m139t745/npm_transitive/{}'.format(node_name))
os.system('rm -rf /dev/shm/npm')