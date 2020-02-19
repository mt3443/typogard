import json
import os
import re
import random

# get all packages
print('Loading packages...', flush=True)
all_packages = open('/volatile/m139t745/npm_dependencies').read().splitlines()
random.shuffle(all_packages)

# remove package names that have already been analyzed
preprocessed = set()
if os.path.exists('/volatile/m139t745/npm_transitive'):
    print('Removing processed packages...', flush=True)

    for f in os.listdir('/volatile/m139t745/npm_transitive'):
        file_contents = open('/volatile/m139t745/npm_transitive/' + f).read()

        for line in file_contents.splitlines():
            package = line.split(',')[0]
            preprocessed.add(package)

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

if not os.path.isdir('/volatile/m139t745/npm_transitive'):
    os.mkdir('/volatile/m139t745/npm_transitive')

if not os.path.isdir('cluster_input'):
    os.mkdir('cluster_input')
else:
    os.system('rm -rf cluster_input/*')

packages_per_core = int(total_packages / total_cores) + 1

# assign packages
print('Assigning packages...', flush=True)
for node in nodes_cores:
    packages_for_this_node = packages_per_core * int(nodes_cores[node])
    f = open('cluster_input/{}'.format(node), 'w')
    for _ in range(packages_for_this_node):
        if (len(all_packages) == 0):
            break
        p = all_packages.pop()
        if p.split(',')[0] in preprocessed:
            continue
        f.write('{}\n'.format(p))
    f.close()

# start clients
for node in nodes_cores:
    os.system('srun -N 1 -n 1 -c {} -w {} --mem-per-cpu=2G -- python3 get_transitive_output.py {} {} &'.format(nodes_cores[node], node, node, nodes_cores[node]))

print('Job started')
