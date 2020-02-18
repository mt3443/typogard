# Generates pypi_transitive_results, shows potential typosquatting targets for all packages and their transitive dependencies

import typosquatting
import sys
import os

node_name = sys.argv[1]

os.system('rm -rf /dev/shm/pypi')
typosquatting.scan_all('cluster_input/{}'.format(node_name), '/dev/shm/pypi/transitive_output')
os.system('cat /dev/shm/pypi/transitive_output >> /volatile/m139t745/pypi_transitive/{}'.format(node_name))
os.system('rm -rf /dev/shm/pypi')