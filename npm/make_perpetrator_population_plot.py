import typosquatting_transitive
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

# total number of packages processed, from _all_docs.json
total_number_of_packages = 1187059

# results pickle file name
output_filename = '../pickle/npm_perp_pop_output.p'

# list of perpetrators output file name
perps_filename = '../data/npm_perpetrators'

# download counts python dictionary pickle name
dl_count_dict_pickle_name = '../pickle/npm_dl_count_dict.p'

if not os.path.exists(output_filename):
    # raw data
    download_counts = pd.read_csv('../data/npm_download_counts.csv')
    dl_count_dict = {}

    if not os.path.exists(dl_count_dict_pickle_name):

        for i in range(len(download_counts)):
            dl_count_dict[download_counts.iloc[i].package_name] = download_counts.iloc[i].weekly_downloads

        pickle.dump(dl_count_dict, open(dl_count_dict_pickle_name, 'wb'))

    else:
        dl_count_dict = pickle.load(open(dl_count_dict_pickle_name, 'rb'))

    # get potential perpetrators
    y = []
    log = open(perps_filename, 'w')

    for i, row in download_counts.iterrows():

        if i % 1000 == 0:
            print('\r{}'.format(i), flush=True, end='')

        package_name = row.package_name
        weekly_downloads = row.weekly_downloads

        targets = typosquatting_transitive.run_tests(str(package_name))

        if targets is not None:
            # tuple structure (perpetrator name, perpetrator download count, most popular target, most popular target download count)
            target_list = list(targets)
            most_popular_target = target_list[0]

            if target_list[0] in dl_count_dict:
                most_popular_target_dl = dl_count_dict[target_list[0]]
            else:
                most_popular_target_dl = 0

            for t in targets:
                if t in dl_count_dict and dl_count_dict[t] > most_popular_target_dl:
                    most_popular_target = t
                    most_popular_target_dl = dl_count_dict[t]

            y.append((package_name, weekly_downloads, most_popular_target, most_popular_target_dl))
            log.write('{},{},{},{}\n'.format(package_name, weekly_downloads, most_popular_target, most_popular_target_dl))

    pickle.dump(y, open(output_filename, 'wb'))
    log.close()

else:
    y = pickle.load(open(output_filename, 'rb'))

points = []

for value in y:
    points.append(value[1])

plt.title('Number of Perpetrators by Popularity (NPM)')
plt.rcParams['figure.figsize'] = (20, 16)
plt.hist(points, bins=[0, 10, 100, 1000, 10000])
plt.xscale('symlog')
plt.xlim(1, 10000)
plt.xlabel('Number of weekly downloads')
plt.ylabel('Number of potential typosquatting perpetrators')
plt.show()
