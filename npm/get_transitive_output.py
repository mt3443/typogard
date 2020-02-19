# Generates npm_transitive_results, shows potential typosquatting targets for all packages and their transitive dependencies

import typosquatting
import sys
import os

node_name = sys.argv[1]
n_threads = int(sys.argv[2])

os.system('rm -rf /dev/shm/npm')
typosquatting.scan_all('cluster_input/{}'.format(node_name), '/volatile/m139t745/npm_transitive/{}'.format(node_name), n_threads)