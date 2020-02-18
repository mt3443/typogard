# Generates pypi_download_counts.csv

import requests
from bs4 import BeautifulSoup
import threading
import os

n_threads = 32
output_filename = '../data/pypi_download_counts.csv'
lock = threading.Lock()

response = requests.get('https://pypi.org/simple/')
soup = BeautifulSoup(response.content, 'html.parser')

all_packages = [x.text for x in soup.find_all('a')]

# remove packages that have already been processed
if os.path.exists(output_filename):
    all_packages = set(all_packages)
    preprocessed = open(output_filename).read().splitlines()[1:]

    for p in preprocessed:
        name = p.split(',')[0]

        if name in all_packages:
            all_packages.remove(name)

    all_packages = list(all_packages)
    log_file = open(output_filename, 'a')

else:
    log_file = open(output_filename, 'a')
    log_file.write('package_name,weekly_downloads\n')

def log(m):
    lock.acquire()
    log_file.write('{}\n'.format(m))
    lock.release()

print('Getting weekly download counts for {} packages'.format(len(all_packages)))

def get_counts(packages):
    for package_name in packages:
        try:
            downloads_response = requests.get('https://pypistats.org/api/packages/{}/recent?period=week'.format(package_name.lower()))

            if downloads_response.status_code != 200:
                print('download count request for {} returned status code {}'.format(package_name, downloads_response.status_code))
                continue

            weekly_downloads = downloads_response.json()['data']['last_week']

            log('{},{}'.format(package_name, weekly_downloads))
        
        except:
            print('Unhandled exception when processing {}'.format(package_name))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

threads = []
all_chunks = chunks(all_packages, int(len(all_packages) / n_threads) + 1)

for _ in range(n_threads):
    chunk = next(all_chunks)
    t = threading.Thread(target=get_counts, args=(chunk,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

log_file.close()