import json
import os
import re
import random
import requests

# get all packages
print('Loading packages...', flush=True)
if not os.path.exists('_all_docs.json'):
	all_docs_request = requests.get('https://replicate.npmjs.com/_all_docs')

	if all_docs_request.status_code != 200:
		print('Error: all_docs request returned status code {}'.format(all_docs_request.status_code))
		exit(1)

	with open('_all_docs.json', 'w') as f:
		f.write(all_docs_request.content)

all_docs = json.load(open('_all_docs.json'))
all_packages = [x['id'] for x in all_docs['rows']]
random.shuffle(all_packages)

# remove package names that have already been analyzed
if os.path.exists('/volatile/m139t745/npm_downloads'):
    print('Removing processed packages...', flush=True)
    all_packages_set = set(all_packages)

    for f in os.listdir('/volatile/m139t745/npm_downloads'):
        file_contents = open('/volatile/m139t745/npm_downloads/' + f).read().splitlines()

        for line in file_contents:
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

unused_nodes = unused_nodes[-130:]

total_cores = 0
total_packages = len(all_packages)
nodes_cores = {}

for node in unused_nodes:
    name = re.findall(r'NodeName=(\S+)', node)[0]
    n_cores = re.findall(r'CPUTot=(\d+)', node)[0]
    nodes_cores[name] = n_cores
    total_cores += int(n_cores)

if not os.path.isdir('/volatile/m139t745/npm_downloads'):
    os.mkdir('/volatile/m139t745/npm_downloads')

if not os.path.isdir('cluster_input'):
    os.mkdir('cluster_input')
else:
    os.system('rm -rf cluster_input/*')

packages_per_node = int(total_packages / len(nodes_cores)) + 1

# assign packages
print('Assigning packages...', flush=True)
for node in nodes_cores:
    f = open('cluster_input/{}'.format(node), 'w')
    for _ in range(packages_per_node):
        if (len(all_packages) == 0):
            break
        f.write('{}\n'.format(all_packages.pop()))
    f.close()

# start clients
for node in nodes_cores:
    os.system('srun -N 1 -n 1 -c {} -w {} --mem-per-cpu=2G python3 get_download_counts.py {} &'.format(nodes_cores[node], node, node))

print('Job started')