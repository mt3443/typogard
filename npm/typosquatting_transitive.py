from itertools import groupby, permutations
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

# check if two packages have the same scope
def same_scope(p1, p2):
    p1_match = scope_regex.match(p1)
    p2_match = scope_regex.match(p2)

    if p1_match is None or p2_match is None:
        return False

    return p1_match.group(1) == p2_match.group(1)

# 'reeaaaccct' => 'react'
def repeated_characters(package_name, return_all=False):
    s = ''.join([i[0] for i in groupby(package_name)])
    
    if s in popular_packages and not same_scope(package_name, s):
        return s

    return None
        
# 'event-streaem' => 'event-stream'
# 'event-stream' => 'event-strem'
def omitted_chars(package_name, return_all=False):
    for i in range(len(package_name) - 1):
        s = package_name[:i] + package_name[(i + 1):]

        if s in popular_packages and not same_scope(package_name, s):
            return s

    return None

# 'loadsh' => 'lodash'
def swapped_characters(package_name, return_all=False):
    for i in range(len(package_name) - 1):
        a = list(package_name)
        t = a[i]
        a[i] = a[i + 1]
        a[i + 1] = t
        s = ''.join(a)

        if s in popular_packages and not same_scope(package_name, s):
            return s

    return None

# 'stream-event' => 'event-stream'
# 'event.stream' => 'event-stream'
# 'de-bug' => 'debug'
def swapped_words(package_name, return_all=False):
    if delimiter_regex.search(package_name) is not None:
        tokens = delimiter_regex.sub(' ', package_name).split()

        if len(tokens) > 8:
            return None

        for p in permutations(tokens):
            for d in delimiters:
                s = d.join(p)

                if s in popular_packages and not same_scope(package_name, s):
                    return s

    return None

# '1odash' => 'lodash'
# 'teqeusts' => 'requests'
def common_typos(package_name, return_all=False):
    for i, c in enumerate(package_name):
        if c in typos:
            for t in typos[c]:
                s = list(package_name)
                s[i] = t
                s = ''.join(s)

                if s in popular_packages and not same_scope(package_name, s):
                    return s

    return None

# 'react-2' => 'react'
# 'react2' => 'react'
def version_numbers(package_name):
    m = version_number_regex.match(package_name)

    if m is not None:
        s = m.group(1)

        if s in popular_packages and not same_scope(package_name, s):
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

        results = list(filter(lambda x: x is not None and x is not '', results))

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

# gets download count for given package
def get_download_count(package_name):
    if packages_df is None:
        scan_all_init()

    if package_name not in packages_df.package_name.values:
        return 0

    return packages_df.loc[packages_df.package_name == package_name].weekly_downloads.values[0]

if __name__ == '__main__':
    import sys
    if sys.argv[1] is None:
        print('Usage: py typosquatting_transitive.py [package_name]')
        exit(1)
    r = run_tests(sys.argv[1])
    if r is not None:
        print('"{}" could be typosquatting {}'.format(sys.argv[1], set(r)))