import json
import os
import re
import random

# get all packages
print('Loading packages...', flush=True)
all_packages = [x.split(',')[0] for x in open('../data/npm_download_counts.csv').read().splitlines()[1:]]
random.shuffle(all_packages)

# remove package names that have already been analyzed
if os.path.exists('/volatile/m139t745/npm_dependencies'):
    print('Removing processed packages...', flush=True)
    all_packages_set = set(all_packages)

    for f in os.listdir('/volatile/m139t745/npm_dependencies'):
        file_contents = open('/volatile/m139t745/npm_dependencies/' + f).read()

        if file_contents[-1] != '\n':
            file_contents = file_contents[:file_contents.rfind('\n')]
            writer = open('/volatile/m139t745/npm_dependencies/' + f, 'w')
            writer.write(file_contents + '\n')
            writer.close()

        for line in file_contents.splitlines():
            package = line.split(',')[0]
            if package in all_packages_set:
                all_packages_set.remove(package)

    all_packages = list(all_packages_set)
    del all_packages_set

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

if not os.path.isdir('/volatile/m139t745/npm_dependencies'):
    os.mkdir('/volatile/m139t745/npm_dependencies')

if not os.path.isdir('npm_dependencies'):
    os.mkdir('npm_dependencies')
else:
    os.system('rm -rf npm_dependencies/*')

packages_per_node = int(total_packages / len(nodes_cores)) + 1

# assign packages
print('Assigning packages...', flush=True)
for node in nodes_cores:
    f = open('npm_dependencies/{}'.format(node), 'w')
    for _ in range(packages_per_node):
        if (len(all_packages) == 0):
            break
        f.write('{}\n'.format(all_packages.pop()))
    f.close()

# start clients
for node in nodes_cores:
    os.system('srun -N 1 -n 1 -c {} -w {} --mem-per-cpu=2G -- node get_npm_dependencies.js {} &'.format(nodes_cores[node], node, node))

print('Job started')
