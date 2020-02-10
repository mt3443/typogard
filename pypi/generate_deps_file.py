from get_pypi_dependencies import get_dependencies
import pandas as pd
import threading

n_threads = 32
df = pd.read_csv('../data/pypi_download_counts.csv')
all_packages = list(df.package_name.values)
lock = threading.Lock()

preprocessed = open('../data/pypi_dependencies').read().splitlines()

all_packages = set(all_packages)
for line in preprocessed:
    name = line.split(',')[0]
    if name in all_packages:
        all_packages.remove(name)
all_packages = list(all_packages)

log_file = open('../data/pypi_dependencies', 'a')

def log(m):
    lock.acquire()
    log_file.write('{}\n'.format(m))
    log_file.flush()
    lock.release()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def start_thread(packages):
    for package_name in packages:
        dependencies = get_dependencies(package_name)

        line = package_name

        for d in dependencies:
            line += ',' + d

        log(line)

all_chunks = chunks(all_packages, int(len(all_packages) / n_threads) + 1)
threads = []

for _ in range(n_threads):
    current_chunk = next(all_chunks)
    t = threading.Thread(target=start_thread, args=(current_chunk,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
