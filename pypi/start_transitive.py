import os
import sys

node = sys.argv[1]

os.system('rm -rf /dev/shm/pypi')
os.system('mkdir -p /dev/shm/pypi/transitive')
os.system('mkdir -p /dev/shm/pypi/data')
os.system('cp /users/m139t745/typosquatting/pypi/typosquatting_transitive.js /dev/shm/pypi/transitive')
os.system('cp /users/m139t745/typosquatting/data/pypi_download_counts.csv /dev/shm/pypi/data')

os.system('node typosquatting_transitive.js {} --max-old-space-size=65535'.format(node))

os.system('rm -rf /dev/shm/pypi')