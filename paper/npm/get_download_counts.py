# Generates npm_download_counts.csv

import requests
import threading
import sys
import time
import os
import json

n_threads = 16
lock = threading.Lock()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if os.path.exists('_all_docs.json'):
	all_packages = [x['id'] for x in json.load(open('_all_docs.json'))['rows']]
else:
	all_packages = [x['id'] for x in requests.get('https://replicate.npmjs.com/_all_docs').json()['rows']]

if os.path.exists('../data/npm_downloads'):
	all_packages = set(all_packages)
	for line in open('../data/npm_downloads').read().splitlines():
		p = line.split(',')[0]
		if p in all_packages:
			all_packages.remove(p)
	all_packages = list(all_packages)

log = open('../data/npm_downloads', 'a')
downloads_url = 'https://api.npmjs.org/downloads/point/last-week/{}'

def get_download_counts(packages):
	for package_name in packages:
		# get download counts
		r = requests.get(downloads_url.format(package_name))

		while r.status_code == 429:
			time.sleep(2)
			r = requests.get(downloads_url.format(package_name))

		if r.status_code == 200:

			weekly_downloads = r.json()['downloads']

			lock.acquire()
			log.write('{},{}\n'.format(package_name, weekly_downloads))
			log.flush()
			lock.release()

		else: 
			
			print('Package {} returned status code {}'.format(package_name, r.status_code))

threads = []
all_chunks = chunks(all_packages, int(len(all_packages) / n_threads) + 1)
for _ in range(n_threads):
	current_chunk = next(all_chunks)
	t = threading.Thread(target=get_download_counts, args=(current_chunk,))
	t.start()
	threads.append(t)

for t in threads:
	t.join()