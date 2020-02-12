import os
import random
import pandas as pd

# get all package names
df = pd.read_csv('../data/pypi_download_counts.csv')
names = list(df.package_name.values)
weights = list(df.weekly_downloads.values)
n = 10000
sample = random.choices(names, weights=weights, k=n)

# write package names to file
f = open('../data/pypi_sample', 'w')
for package_name in sample:
    f.write('{}\n'.format(package_name))
f.close()

# start scanner
os.system('node sample_scanner.js')