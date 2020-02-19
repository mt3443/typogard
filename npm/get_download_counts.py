import requests
import threading
import sys
import time

node_name = sys.argv[1]
n_threads = 8
lock = threading.Lock()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

all_packages = open('/users/m139t745/typosquatting/npm/cluster_input/{}'.format(node_name)).read().splitlines()

log = open('/volatile/m139t745/npm_downloads/{}'.format(node_name), 'w')
counter = 0
downloads_url = 'https://api.npmjs.org/downloads/point/last-week/{}'

def t(packages):
	for package_name in packages:
		# get download counts
		try:
			r = requests.get(downloads_url.format(package_name))

			while r.status_code == 429:
				time.sleep(30)
				r = requests.get(downloads_url.format(package_name))

			if r.status_code == 200:

				weekly_downloads = r.json()['downloads']

				lock.acquire()
				log.write('{},{}\n'.format(package_name, weekly_downloads))
				counter += 1
				if counter == 100:
					log.flush()
					counter = 0
				lock.release()

		except:
			continue

threads = []
all_chunks = chunks(all_packages, int(len(all_packages) / n_threads) + 1)
for _ in range(n_threads):
	current_chunk = next(all_chunks)
	t = threading.Thread(target=t, args=(current_chunk,))
	t.start()
	threads.append(t)

for t in threads:
	t.join()