from itertools import groupby, permutations
import re

delimiter_regex = re.compile('[\-|\.|_]')
delimiters = ['', '.', '-', '_']

version_number_regex = re.compile('^(.*?)[\.|\-|_]?\d+$')

scope_regex = re.compile('^@(.*?)/.+$')

typos = {
    '@': ['', '2', 'a', '1', 'q', 'w', 'e', '3'],
    '1': ['2', 'w', 'q', 'i', 'l'],
    '2': ['1', 'q', 'w', 'e', '3'],
    '3': ['2', 'w', 'e', 'r', '4'],
    '4': ['3', 'e', 'r', 't', '5', 'a'],
    '5': ['4', 'r', 't', 'y', '6', 's'],
    '6': ['5', 't', 'y', 'u', '7'],
    '7': ['6', 'y', 'u', 'i', '8'],
    '8': ['7', 'u', 'i', 'o', '9'],
    '9': ['8', 'i', 'o', 'p', '0'],
    '0': ['9', 'o', 'p', '-', '_'],
    '-': ['_', '0', 'p', '.', ''],
    '_': ['-', '0', 'p', '.', ''],
    'q': ['1', '2', 'w', 's', 'a'],
    'w': ['1', '2', '3', 'e', 'd', 's', 'a', 'q', 'vv'],
    'e': ['2', '3', '4', 'r', 'f', 'd', 's', 'w'],
    'r': ['3', '4', '5', 't', 'g', 'f', 'd', 'e'],
    't': ['4', '5', '6', 'y', 'h', 'g', 'f', 'r'],
    'y': ['5', '6', '7', 'u', 'j', 'h', 'g', 't', 'i'],
    'u': ['6', '7', '8', 'i', 'k', 'j', 'h', 'y', 'v'],
    'i': ['1', '7', '8', '9', 'o', 'l', 'k', 'j', 'u', 'y'],
    'o': ['8', '9', '0', 'p', 'l', 'k', 'i'],
    'p': ['9', '0', '-', '_', 'l', 'o'],
    'a': ['q', 'w', 's', 'x', 'z'],
    's': ['q', 'w', 'e', 'd', 'c', 'x', 'z', 'a', '5'],
    'd': ['w', 'e', 'r', 'f', 'v', 'c', 'x', 's'],
    'f': ['e', 'r', 't', 'g', 'b', 'v', 'c', 'd'],
    'g': ['r', 't', 'y', 'h', 'n', 'b', 'v', 'f'],
    'h': ['t', 'y', 'u', 'j', 'm', 'n', 'b', 'g'],
    'j': ['y', 'u', 'i', 'k', 'm', 'n', 'h'],
    'k': ['u', 'i', 'o', 'l', 'm', 'j'],
    'l': ['i', 'o', 'p', 'k', '1'],
    'z': ['a', 's', 'x'],
    'x': ['z', 'a', 's', 'd', 'c'],
    'c': ['x', 's', 'd', 'f', 'v'],
    'v': ['c', 'd', 'f', 'g', 'b', 'u'],
    'b': ['v', 'f', 'g', 'h', 'n'],
    'n': ['b', 'g', 'h', 'j', 'm'],
    'm': ['n', 'h', 'j', 'k', 'rn'],
    '.': ['-', '_', ''],
    '/': ['1', 'l', 'i']
}

popular_packages = set(open('../data/pypi_popular_packages').read().splitlines())

# check if two packages have the same scope
def same_scope(p1, p2):
    p1_match = scope_regex.match(p1)
    p2_match = scope_regex.match(p2)

    if p1_match is None or p2_match is None:
        return False

    return p1_match.group(1) == p2_match.group(1)

# 'reeaaaccct' => 'react'
def repeated_characters(package_name):
    s = ''.join([i[0] for i in groupby(package_name)])
    
    if s in popular_packages and not same_scope(package_name, s):
        return s

    return None
        
# 'event-streaem' => 'event-stream'
# 'event-stream' => 'event-strem'
def omitted_chars(package_name):
    for i in range(len(package_name) - 1):
        s = package_name[:i] + package_name[(i + 1):]

        if s in popular_packages and not same_scope(package_name, s):
            return s

    return None

# 'loadsh' => 'lodash'
def swapped_characters(package_name):
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
def swapped_words(package_name):
    if delimiter_regex.search(package_name) is not None:
        tokens = delimiter_regex.sub(' ', package_name).split()

        for p in permutations(tokens):
            for d in delimiters:
                s = d.join(p)

                if s in popular_packages and not same_scope(package_name, s):
                    return s

    return None

# '1odash' => 'lodash'
# 'teqeusts' => 'requests'
def common_typos(package_name):
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

        results = list(filter(lambda x: x is not None, results))

        if len(results) != 0:
            return results

    return None

if __name__ == '__main__':
    import sys
    if sys.argv[1] is None:
        print('Usage: py typosquatting_transitive.py [package_name]')
        exit(1)
    r = run_tests(sys.argv[1])
    if r is not None:
        print('"{}" could be typosquatting {}'.format(sys.argv[1], set(r)))