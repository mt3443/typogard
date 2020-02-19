import os
import random
import pandas as pd
import subprocess
import typosquatting

# get all package names
df = pd.read_csv('../data/npm_download_counts.csv')
names = list(df.package_name.values)
weights = list(df.weekly_downloads.values)
n = 10000
sample = random.choices(names, weights=weights, k=n)
output_file = open('../data/npm_sample', 'w')

for package_name in sample:
    stdout = subprocess.check_output('node get_npm_deps_cli.js {}'.format(package_name), shell=True).decode('utf8')
    dependencies = stdout.split('Dependencies:\n')[1].splitlines()
    alert = False
    for d in dependencies:
        if typosquatting.run_tests(d) is not None:
            alert = True
            break
    
    output_file.write('{},{}\n'.format(package_name, 'yes' if alert else 'no'))
    output_file.flush()

output_file.close()