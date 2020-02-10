import json
import os
import re
import random
import pandas as pd

# get all packages
print('Loading packages...', flush=True)
df = pd.read_csv('../data/pypi_download_counts.csv')
all_packages = list(df.package_name.values)
random.shuffle(all_packages)

# remove package names that have already been analyzed
if os.path.exists('/volatile/m139t745/pypi_transitive_output'):
    print('Removing processed packages...', flush=True)
    all_packages_set = set(all_packages)

    for f in os.listdir('/volatile/m139t745/pypi_transitive_output'):
        file_contents = open('/volatile/m139t745/pypi_transitive_output/' + f).read()

        if file_contents[-1] != '\n':
            file_contents = file_contents[:file_contents.rfind('\n')]
            writer = open('/volatile/m139t745/pypi_transitive_output/' + f, 'w')
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

if not os.path.isdir('/volatile/m139t745/pypi_transitive_output'):
    os.mkdir('/volatile/m139t745/pypi_transitive_output')

if not os.path.isdir('transitive_package_names'):
    os.mkdir('transitive_package_names')
else:
    os.system('rm -rf transitive_package_names/*')

packages_per_core = int(total_packages / total_cores) + 1

# assign packages
print('Assigning packages...', flush=True)
for node in nodes_cores:
    packages_for_this_node = packages_per_core * int(nodes_cores[node])
    f = open('transitive_package_names/{}'.format(node), 'w')
    for _ in range(packages_for_this_node):
        if (len(all_packages) == 0):
            break
        f.write('{}\n'.format(all_packages.pop()))
    f.close()

# start clients
for node in nodes_cores:
    os.system('srun -N 1 -n 1 -c {} -w {} --mem-per-cpu=2G -- python3 start_transitive.py {} {} &'.format(nodes_cores[node], node, node, nodes_cores[node]))

print('Job started')
