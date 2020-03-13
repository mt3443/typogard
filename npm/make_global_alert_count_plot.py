# Generates plot showing the percentage of all weekly downloads containing a typosquatting package
# as a function of popularity threshold

import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

import sys

if sys.argv[1] is None:
    exit()

# results pickle file name
output_filename = '../pickle/npm_global_alert_output_{}.p'.format(sys.argv[1])
output_filename_pypi = '../pickle/pypi_global_alert_output_{}.p'.format(sys.argv[1])

# download counts python dictionary pickle name
dl_count_dict_pickle_name = '../pickle/npm_dl_count_dict.p'

total_npm_weekly_downloads = 17000000000

if not os.path.exists(output_filename):

    # x axis values, popularity threshold
    x_begin = 350
    x_end = 1000000
    x = list(range(x_begin, x_end, int((x_end - x_begin) / 100)))

    # raw data
    results = open('../data/npm_transitive_results').read().splitlines()
    download_counts = pd.read_csv('../data/npm_download_counts.csv', na_filter=False)
    dl_count_dict = {}

    if not os.path.exists(dl_count_dict_pickle_name):

        for i in range(len(download_counts)):
            dl_count_dict[download_counts.iloc[i].package_name] = download_counts.iloc[i].weekly_downloads

        pickle.dump(dl_count_dict, open(dl_count_dict_pickle_name, 'wb'))

    else:
        dl_count_dict = pickle.load(open(dl_count_dict_pickle_name, 'rb'))

    # percentage of packages typosquatting
    y = []

    # total number of packages processed
    total_number_of_packages = len(dl_count_dict)

    for threshold in x:
        print(threshold, flush=True)
        
        popular_dl_count = threshold

        # find number of packages that could be typosquatting something above the threshold
        count = 0
        for result in results:
            tokens = result.split(',')

            if len(tokens) == 1:
                continue

            package_name = tokens[0]
            dependency_names = tokens[1::2]
            typosquatting_names = tokens[2::2]

            for d, t in zip(dependency_names, typosquatting_names):
                
                # check if the dependency is popular
                if d in dl_count_dict:
                    d_dl_count = dl_count_dict[d]
                else:
                    d_dl_count = 0

                # if the dependency is popular, move on
                if d_dl_count >= popular_dl_count:
                    continue

                # check how popular the package being "typosquatted" is
                if t in dl_count_dict:
                    t_dl_count = dl_count_dict[t]
                else:
                    t_dl_count = 0

                # if the "typosquatted" package is popular, count it
                if t_dl_count >= popular_dl_count:
                    
                    # add however popular the overall package is to the running total
                    if package_name in dl_count_dict:
                        count += dl_count_dict[package_name]
                    else:
                        count += 1

                    # dont count the same package twice
                    break

        y.append(count / total_npm_weekly_downloads * 100)

    pickle.dump((x_begin, x_end, x, y), open(output_filename, 'wb'))

else:
    x_begin, x_end, x, y = pickle.load(open(output_filename, 'rb'))
    pypi_x_begin, pypi_x_end, pypi_x, pypi_y = pickle.load(open(output_filename_pypi, 'rb'))

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

x = np.array(x)
y = np.array(y)

poly_reg = PolynomialFeatures()
x_poly = poly_reg.fit_transform(x.reshape(-1, 1))
y_poly = LinearRegression().fit(x_poly, y.reshape(-1, 1)).predict(x_poly)

pypi_x = np.array(pypi_x)
pypi_y = np.array(pypi_y)

poly_reg = PolynomialFeatures()
pypi_x_poly = poly_reg.fit_transform(pypi_x.reshape(-1, 1))
pypi_y_poly = LinearRegression().fit(pypi_x_poly, pypi_y.reshape(-1, 1)).predict(pypi_x_poly)

plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams.update({'font.size': 18})
plt.plot(x, y, color='red', label='npm')
# plt.plot(x, y_poly)
plt.plot(pypi_x, pypi_y, color='blue', label='PyPI')
# plt.title('Percentage of Downloads that Trigger Alerts vs Popularity')
plt.xlabel('Popularity Threshold (Weekly Downloads)')
plt.ylabel('Typosquatting Downloads (% of All Downloads)')
plt.xlim(x_begin, x_end)
plt.legend()
plt.show()
