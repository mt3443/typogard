# Gets dependency tree statistics for npm

from statistics import mean, median, mode
import pickle

dls = pickle.load(open('../pickle/npm_dl_count_dict.p', 'rb'))

packages = open('../data/npm_dependencies').read().splitlines()

depednency_tree_sizes = []

for p in packages:
    if ',' not in p or (p.split(',')[0] in dls and dls[p.split(',')[0]] <= 350):
        continue
    depednencies = p.split(',')[1:]
    depednency_tree_sizes.append(len(depednencies))

print('mean', mean(depednency_tree_sizes))
print('median', median(depednency_tree_sizes))
print('mode', mode(depednency_tree_sizes))