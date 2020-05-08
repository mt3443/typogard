import time
import requests
import threading
import sys

node_name = sys.argv[1]
n_threads = int(sys.argv[2])

all_lines = open('/volatile/m139t745/rubygems/input/{}'.format(node_name)).read().splitlines()
output = open('/volatile/m139t745/rubygems/output/{}'.format(node_name), 'a')
lock = threading.Lock()

def thread_target(lines):
	for line in lines:
		package = line.split()[0]
		version = line.split()[1].replace('(', '').replace(')', '')

		dependencies = set([package])
		todo = [package]

		while len(todo) != 0:
			package_name = todo.pop(0)

			r = requests.get('https://api.rubygems.org/api/v1/dependencies.json?gems={}'.format(package_name))

			while r.status_code == 429:
				time.sleep(30)
				r = requests.get('https://api.rubygems.org/api/v1/dependencies.json?gems={}'.format(package_name))

			if r.status_code != 200:
				print('DEPENDENCY REQUEST FOR {} RETURNED STATUS CODE {}'.format(package_name, r.status_code))
			else:
				try:
					metadata = r.json()[0]
					for d in metadata['dependencies']:
						dependencies.add(d[0])
						todo.append(d[0])
				except:
					print('Unhandled exception when processing {}'.format(package_name))
		
		lock.acquire()
		output.write('{},{}\n'.format(package, ','.join(list(dependencies))))
		output.flush()
		lock.release()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

all_chunks = chunks(all_lines, int(len(all_lines) / n_threads) + 1)

threads = []
for _ in range(n_threads):
	current_chunk = next(all_chunks)
	t = threading.Thread(target=thread_target, args=(current_chunk,))
	t.start()
	threads.append(t)

for t in threads:
	t.join()

output.close()