from itertools import groupby, permutations
from functools import lru_cache
import re

delimiter_regex = re.compile('[\-|\.|_]')
delimiters = ['', '.', '-', '_']

version_number_regex = re.compile('^(.*?)[\.|\-|_]?\d$')

scope_regex = re.compile('^@(.*?)/.+$')

typos = {
    '1': ['2', 'q', 'i', 'l'],
    '2': ['1', 'q', 'w', '3'],
    '3': ['2', 'w', 'e', '4'],
    '4': ['3', 'e', 'r', '5'],
    '5': ['4', 'r', 't', '6', 's'],
    '6': ['5', 't', 'y', '7'],
    '7': ['6', 'y', 'u', '8'],
    '8': ['7', 'u', 'i', '9'],
    '9': ['8', 'i', 'o', '0'],
    '0': ['9', 'o', 'p', '-'],
    '-': ['_', '0', 'p', '.', ''],
    '_': ['-', '0', 'p', '.', ''],
    'q': ['1', '2', 'w', 'a'],
    'w': ['2', '3', 'e', 's', 'a', 'q', 'vv'],
    'e': ['3', '4', 'r', 'd', 's', 'w'],
    'r': ['4', '5', 't', 'f', 'd', 'e'],
    't': ['5', '6', 'y', 'g', 'f', 'r'],
    'y': ['6', '7', 'u', 'h', 't', 'i'],
    'u': ['7', '8', 'i', 'j', 'y', 'v'],
    'i': ['1', '8', '9', 'o', 'l', 'k', 'j', 'u', 'y'],
    'o': ['9', '0', 'p', 'l', 'i'],
    'p': ['0', '-', 'o'],
    'a': ['q', 'w', 's', 'z'],
    's': ['w', 'd', 'x', 'z', 'a', '5'],
    'd': ['e', 'r', 'f', 'c', 'x', 's'],
    'f': ['r', 'g', 'v', 'c', 'd'],
    'g': ['t', 'h', 'b', 'v', 'f'],
    'h': ['y', 'j', 'n', 'b', 'g'],
    'j': ['u', 'i', 'k', 'm', 'n', 'h'],
    'k': ['i', 'o', 'l', 'm', 'j'],
    'l': ['i', 'o', 'p', 'k', '1'],
    'z': ['a', 's', 'x'],
    'x': ['z', 's', 'd', 'c'],
    'c': ['x', 'd', 'f', 'v'],
    'v': ['c', 'f', 'g', 'b', 'u'],
    'b': ['v', 'g', 'h', 'n'],
    'n': ['b', 'h', 'j', 'm'],
    'm': ['n', 'j', 'k', 'rn'],
    '.': ['-', '_', '']
}

# Set containing the names of all packages considered to be popular
popular_packages = set(open('../data/npm_popular_packages').read().splitlines())

# pandas dataframe containing the names and download counts of all packages, call scan_all_init to initialize
packages_df = None
all_packages = None

# check if two packages have the same scope
def same_scope(p1, p2):
    p1_match = scope_regex.match(p1)
    p2_match = scope_regex.match(p2)

    if p1_match is None or p2_match is None:
        return False

    return p1_match.group(1) == p2_match.group(1)

# 'reeaaaccct' => 'react'
def repeated_characters(package_name, package_list=popular_packages):
    s = ''.join([i[0] for i in groupby(package_name)])
    
    if s in package_list and not same_scope(package_name, s) and s != package_name:
        return s

    return None
        
# 'event-streaem' => 'event-stream'
# 'event-stream' => 'event-strem'
def omitted_chars(package_name, return_all=False, package_list=popular_packages):

    if len(package_name) < 7:
        return None

    if return_all:
        candidates = []

    for i in range(len(package_name)):
        s = package_name[:i] + package_name[(i + 1):]

        if s in package_list and not same_scope(package_name, s) and s != package_name:
            if return_all:
                candidates.append(s)
            else:
                return s

    if return_all and candidates != []:
        return candidates

    return None

# 'loadsh' => 'lodash'
def swapped_characters(package_name, return_all=False, package_list=popular_packages):

    if return_all:
        candidates = []

    for i in range(len(package_name) - 1):
        a = list(package_name)
        t = a[i]
        a[i] = a[i + 1]
        a[i + 1] = t
        s = ''.join(a)

        if s in package_list and not same_scope(package_name, s) and s != package_name:
            if return_all:
                candidates.append(s)
            else:
                return s

    if return_all and candidates != []:
        return candidates

    return None

# 'stream-event' => 'event-stream'
# 'event.stream' => 'event-stream'
# 'de-bug' => 'debug'
def swapped_words(package_name, return_all=False, package_list=popular_packages):

    if return_all:
        candidates = []

    if delimiter_regex.search(package_name) is not None:
        tokens = delimiter_regex.sub(' ', package_name).split()

        if len(tokens) > 8:
            return None

        for p in permutations(tokens):
            for d in delimiters:
                s = d.join(p)

                if s in package_list and not same_scope(package_name, s) and s != package_name:
                    if return_all:
                        candidates.append(s)
                    else:
                        return s

    if return_all and candidates != []:
        return candidates

    return None

# '1odash' => 'lodash'
# 'teqeusts' => 'requests'
def common_typos(package_name, return_all=False, package_list=popular_packages):

    if return_all:
        candidates = []

    for i, c in enumerate(package_name):
        if c in typos:
            for t in typos[c]:
                s = list(package_name)
                s[i] = t
                s = ''.join(s)

                if s in package_list and not same_scope(package_name, s) and s != package_name:
                    if return_all:
                        candidates.append(s)
                    else:
                        return s

    if return_all and candidates != []:
        return candidates

    return None

# 'react-2' => 'react'
# 'react2' => 'react'
def version_numbers(package_name, package_list=popular_packages):
    m = version_number_regex.match(package_name)

    if m is not None:
        s = m.group(1)

        if s in package_list and not same_scope(package_name, s) and s != package_name:
            return s

    return None

# run all tests on given package name, return potential typosquatting targets
def run_tests(package_name):
    if package_name not in popular_packages:

        results = [
            repeated_characters(package_name),
            omitted_chars(package_name),
            swapped_characters(package_name),
            swapped_words(package_name),
            common_typos(package_name),
            version_numbers(package_name)
        ]

        # remove None's
        results = list(filter(lambda x: x is not None and x is not '', results))

        # flatten
        r = []
        for s in results:
            if type(s) == list:
                for e in s:
                    r.append(e)
            else:
                r.append(s)

        results = list(set(r))

        if len(results) != 0:
            return results

    return None

# run all tests on given package name, return potential typosquatting targets
def run_tests_show_all(package_name):

    if all_packages is None:
        scan_all_init()

    results = [
        repeated_characters(package_name, package_list=all_packages),
        omitted_chars(package_name, return_all=True, package_list=all_packages),
        swapped_characters(package_name, return_all=True, package_list=all_packages),
        swapped_words(package_name, return_all=True, package_list=all_packages),
        common_typos(package_name, return_all=True, package_list=all_packages),
        version_numbers(package_name, package_list=all_packages)
    ]

    # remove None's
    results = list(filter(lambda x: x is not None and x is not '', results))

    # flatten
    r = []
    for s in results:
        if type(s) == list:
            for e in s:
                r.append(e)
        else:
            r.append(s)

    results = list(set(r))

    if len(results) != 0:
        return results

    return None

# get results corresponding to each signal
def run_tests_get_signals(package_name):
    if package_name not in popular_packages:

        return {
            'repeated_chars': repeated_characters(package_name),
            'omitted_chars': omitted_chars(package_name),
            'swapped_chars': swapped_characters(package_name),
            'swapped_words': swapped_words(package_name),
            'common_typos': common_typos(package_name),
            'version_numbers': version_numbers(package_name)
        }
    
    else:

        return None

# set up tools required for scanning all packages
def scan_all_init():
    global pd
    import pandas as pd

    global packages_df
    packages_df = pd.read_csv('../data/npm_download_counts.csv')

    global all_packages
    all_packages = set(packages_df.package_name.values)

    global threading
    import threading

    global lock
    lock = threading.Lock()

# gets download count for given package
def get_download_count(package_name):
    if packages_df is None:
        scan_all_init()

    if package_name not in packages_df.package_name.values:
        return 0

    return packages_df.loc[packages_df.package_name == package_name].weekly_downloads.values[0]

# split list into evenly sized chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# returns the most popular package with a name that could be typosquatting the given package
@lru_cache(maxsize=10000)
def get_most_popular_candidate(package_name):
    candidates = run_tests_show_all(package_name)

    if candidates is None:
        return None

    # get most popular target
    most_popular_candidate = candidates[0]
    popularity = get_download_count(candidates[0])
    for c in candidates:
        if get_download_count(c) > popularity:
            most_popular_candidate = c
            popularity = get_download_count(c)

    return most_popular_candidate

# thread target function used to scan all packages
def scan_all_thread_target(lines, log):
    for line in lines:
        tokens = line.split(',')
        package_name = tokens[0]
        dependencies = tokens[1:]

        final_string = package_name

        for dependency in dependencies:
            
            candidate = get_most_popular_candidate(dependency)

            if candidate is not None:
                final_string += (',' + dependency + ',' + candidate)

        final_string += '\n'

        lock.acquire()
        log.write(final_string)
        lock.release()

# scan all pacakges for transitive results
def scan_all(dependencies_filename, transitive_output_filename):
    
    if all_packages is None:
        scan_all_init()

    n_threads = 16
    threads = []

    # get most popular typosquatting target for every package in the given list
    lines = open(dependencies_filename).read().splitlines()
    log = open(transitive_output_filename, 'w')
    all_chunks = chunks(lines, int(len(lines) / n_threads) + 1)

    for _ in range(n_threads):
        current_chunk = next(all_chunks)
        t = threading.Thread(target=scan_all_thread_target, args=(current_chunk,log,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log.close()

# get signal count statistics
def get_signal_counts():
    
    if all_packages is None:
        scan_all_init()

    log = open('../data/npm_signal_counts', 'w')
    log.write('package_name,repeated_characters,omitted_characters,swapped_characters,swapped_words,common_typos,version_numbers\n')

    for package in all_packages:
        package_name = str(package)
        results = run_tests_get_signals(package_name)

        if results is not None:
            if set(results.values()) != {None}:
                final_string = package_name
                final_string += ',' + ','.join(['n/a' if x is None else x for x in results.values()])
                final_string += '\n'

                log.write(final_string)

    log.close()


if __name__ == '__main__':
    import sys
    if sys.argv[1] is None:
        print('Usage: py typosquatting_transitive.py [package_name]')
        exit(1)
    r = run_tests(sys.argv[1])
    if r is not None:
        print('"{}" could be typosquatting {}'.format(sys.argv[1], set(r)))