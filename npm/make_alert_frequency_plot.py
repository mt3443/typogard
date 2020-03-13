import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

import sys

if sys.argv[1] is None:
    exit()

# file name for pickled results
output_filename = '../pickle/npm_alert_frequency_plot_{}.p'.format(sys.argv[1])
output_filename_pypi = '../pickle/pypi_alert_frequency_plot_{}.p'.format(sys.argv[1])

# download count dict pickled object
dl_count_dict_pickle_name = '../pickle/npm_dl_count_dict.p'

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
                    count += 1

                    # move on, 1 package with 10 possibly typosquatting dependencies is 1 alert, not 10
                    break

        y.append(count / total_number_of_packages * 100)

    pickle.dump((x_begin, x_end, x, y), open(output_filename, 'wb'))

else:
    npm_x_begin, npm_x_end, npm_x, npm_y = pickle.load(open(output_filename, 'rb'))
    pypi_x_begin, pypi_x_end, pypi_x, pypi_y = pickle.load(open(output_filename_pypi, 'rb'))

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

npm_x = np.array(npm_x)
npm_y = np.array(npm_y)

poly_reg = PolynomialFeatures()
npm_x_poly = poly_reg.fit_transform(npm_x.reshape(-1, 1))
npm_y_poly = LinearRegression().fit(npm_x_poly, npm_y.reshape(-1, 1)).predict(npm_x_poly)

pypi_x = np.array(pypi_x)
pypi_y = np.array(pypi_y)

poly_reg = PolynomialFeatures()
pypi_x_poly = poly_reg.fit_transform(pypi_x.reshape(-1, 1))
pypi_y_poly = LinearRegression().fit(pypi_x_poly, pypi_y.reshape(-1, 1)).predict(pypi_x_poly)

plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams.update({'font.size': 18})
plt.plot(npm_x, npm_y, color='red', label='npm')
# plt.plot(npm_x, npm_y_poly)
plt.plot(pypi_x, pypi_y, color='blue', label='PyPI')
# plt.title('Percent Typosquatting vs Target Popularity')
plt.xlabel('Popularity Threshold (Weekly Downloads)')
plt.ylabel('Typosquatting Perpetrators (% of All Packages)')
plt.xlim(npm_x_begin, npm_x_end)
plt.legend()
plt.show()
