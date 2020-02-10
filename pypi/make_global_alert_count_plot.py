import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

# total number of packages processed, from _all_docs.json
total_number_of_packages = 204276

# results pickle file name
output_filename = '../pickle/pypi_global_alert_output.p'

# download counts python dictionary pickle name
dl_count_dict_pickle_name = '../pickle/pypi_dl_count_dict.p'

# percentage of top packages to be considered popular
x = list(range(0, 101))

if not os.path.exists(output_filename):
    # raw data
    results = open('../data/pypi_transitive_results').read().splitlines()
    download_counts = pd.read_csv('../data/pypi_download_counts.csv')
    dl_count_dict = {}

    if not os.path.exists(dl_count_dict_pickle_name):

        for i in range(len(download_counts)):
            dl_count_dict[download_counts.iloc[i].package_name] = download_counts.iloc[i].weekly_downloads

        pickle.dump(dl_count_dict, open(dl_count_dict_pickle_name, 'wb'))

    else:
        dl_count_dict = pickle.load(open(dl_count_dict_pickle_name, 'rb'))

    # percentage of packages typosquatting
    y = []

    for percentage in x:
        print(percentage, flush=True)
        # get popularity cutoff package
        threshold = int(total_number_of_packages * (percentage / 100))

        if percentage in [99, 100]:
            popular_dl_count = 0
        else:
            popular_dl_count = download_counts.iloc[threshold]['weekly_downloads']

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

        y.append(count)

    pickle.dump(y, open(output_filename, 'wb'))

else:
    y = pickle.load(open(output_filename, 'rb'))

plt.rcParams['figure.figsize'] = (10, 8)
plt.plot(x, y)
plt.title('Global Weekly Alerts (PyPI)')
plt.xlabel('Percentage of packages considered popular')
plt.ylabel('Number of alerts per week')
plt.xlim(0, 100)
plt.ylim(0, 5e7)
plt.show()
