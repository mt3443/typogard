# Picks a number of packages at random and checks for typosquatting

import os
from numpy.random import choice
import pandas as pd
from get_pypi_dependencies import get_dependencies
import typosquatting

# get all package names
df = pd.read_csv('../data/pypi_download_counts.csv')
names = list(df.package_name.values)
weights = list(df.weekly_downloads.values)
weights_total = sum(weights)
for i, v in enumerate(weights):
    weights[i] = v / weights_total
n = 10000
sample = choice(names, n, False, weights)
output_file = open('../data/pypi_sample', 'w')

for package_name in sample:
    dependencies = get_dependencies(package_name)
    alert = False
    for d in dependencies:
        if typosquatting.run_tests(d) is not None:
            alert = True
            break
    
    output_file.write('{},{}\n'.format(package_name, 'yes' if alert else 'no'))
    output_file.flush()

output_file.close()