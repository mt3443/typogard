import os
import subprocess
from time import perf_counter
import random
import pandas as pd
import re

# set seed for reproducable results
random.seed(0)

# import data
dl_counts = pd.read_csv('../data/downloads.csv')

# format data
package_names = list(dl_counts.package_name.values)
weights = list(dl_counts.weekly_downloads.values)
packages_to_test = random.choices(package_names, weights=weights, k=1000)

# open log file
log_file = open('timing_results.csv', 'w')
log_file.write('package_name,total_packages_installed,normal_time,typosquatting_time,difference,overhead\n')
log_file.flush()

# move to working dir
os.chdir('C:/')

for package in packages_to_test:
    # cache
    os.system('C:\\Users\\Matthew\\Desktop\\nodejs\\npm install "{}"'.format(package))

    # uninstall
    os.system('rm -rf node_modules package-lock.json')

    # test typosquatting
    typosquatting_start = perf_counter()
    output = subprocess.check_output('C:\\Users\\Matthew\\Desktop\\nodejs_typosquatting\\npm install "{}"'.format(package), shell=True)
    typosquatting_stop = perf_counter()

    n_packages_installed = int(re.search(r'total packages installed=(\d+)', output.decode('utf8')).group(1))

    # uninstall
    os.system('rm -rf node_modules package-lock.json')

    # test normal
    normal_start = perf_counter()
    subprocess.check_output('C:\\Users\\Matthew\\Desktop\\nodejs\\npm install "{}"'.format(package), shell=True)
    normal_stop = perf_counter()

    # uninstall
    os.system('rm -rf node_modules package-lock.json')

    # record results
    normal_time = normal_stop - normal_start
    typosquatting_time = typosquatting_stop - typosquatting_start
    difference = typosquatting_time - normal_time
    percent_overhead = difference / normal_time
    log_file.write('{},{},{},{},{},{}\n'.format(package, n_packages_installed, normal_time, typosquatting_time, difference, percent_overhead))
    log_file.flush()