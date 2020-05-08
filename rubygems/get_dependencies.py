# Looks for typosquatting in the transitive dependencies of all packages for PyPI

import json
import os
import re
import random

# get all packages
print('Loading packages...', flush=True)
all_packages = open('/users/m139t745/typosquatting/data/rubygems_package_names').read().splitlines()
random.shuffle(all_packages)

print('Getting cluster info...', flush=True)
os.system('scontrol show node > node_info')
node_info = open('node_info', 'r').readlines()

all_nodes = []

current_node = ''

for line in node_info:
    if line == '\n':
        all_nodes.append(current_node)
        current_node = ''
    else:
        current_node += line

os.system('rm node_info')

unused_nodes = []

for node in all_nodes:
    if 'CPUAlloc=0' in node and 'NodeName=g' not in node and 'NodeName=m' not in node and 'amd' not in node:
        unused_nodes.append(node)

del all_nodes

unused_nodes = unused_nodes[-120:]

total_cores = 0
total_packages = len(all_packages)
nodes_cores = {}

for node in unused_nodes:
    name = re.findall(r'NodeName=(\S+)', node)[0]
    n_cores = re.findall(r'CPUTot=(\d+)', node)[0]
    nodes_cores[name] = n_cores
    total_cores += int(n_cores)

packages_per_core = int(total_packages / total_cores) + 1

# assign packages
print('Assigning packages...', flush=True)
for node in nodes_cores:
    packages_for_this_node = packages_per_core * int(nodes_cores[node])
    f = open('/volatile/m139t745/rubygems/input/{}'.format(node), 'w')
    for _ in range(packages_for_this_node):
        if (len(all_packages) == 0):
            break
        p = all_packages.pop()
        f.write('{}\n'.format(p))
    f.close()

# start clients
for node in nodes_cores:
    os.system('srun -N 1 -n 1 -c {} -w {} --mem-per-cpu=2G -- python3 dependency_getter.py {} {} &'.format(nodes_cores[node], node, node, nodes_cores[node]))

print('Job started')
