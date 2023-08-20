#-------------------------------------------------------------------------
#   Name:
#       TypoGard
#
#   Description:
#       Applies a set of transformations to a given npm package name and
#       the names of all (if any) of that package's transitive
#       dependencies in an attempt to detect typosquatting attacks.
#
#   Usage:
#       py typogard_npm.py [popular_package_list_filename] [package_name]
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#                               IMPORTS
#-------------------------------------------------------------------------
import re
import os
import sys
import subprocess
from typing import List
from itertools import permutations

#-------------------------------------------------------------------------
#                              CONSTANTS
#-------------------------------------------------------------------------

# Delimiters allowed by npm
delimiter_regex = re.compile('[\-|\.|_]')
delimiters = ['', '.', '-', '_']

# Basic regular expression for version numbers after a package name
version_number_regex = re.compile('^(.*?)[\.|\-|_]?\d$')

# Regular expression used to detect npm package name scope
scope_regex = re.compile('^@(.*?)/.+$')

# List of characters allowed in a package name
allowed_characters = 'abcdefghijklmnopqrstuvwxyz1234567890.-_'

# Dictionary containing reasonable typos for each of the allowed
# characters based on QWERTY keyboard locality and visual
# similarity
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

#-------------------------------------------------------------------------
#                               GLOBALS
#-------------------------------------------------------------------------
popular_package_list = None
popular_package_set = None

#-------------------------------------------------------------------------
#                              FUNCTIONS
#-------------------------------------------------------------------------

def get_most_popular_package(packages: List[str]) -> str:
    """
    Returns the most popular package in the given list 'packages'. The most popular
    package is whichever one comes first in the user-specified list of popular packages
    """
    
    # Convert packages to a set for faster lookups
    packages_set = set(packages)

    # Loop through all popular packages
    for popular_package in popular_package_list:

        # Check if the current popular_package is in the given package list
        if popular_package in packages_set:
            
            # If it is, return the popular package name
            return popular_package

    # If we couldn't find any of the given packages in the popular_package_list,
    # just return the first package in the list by default
    return packages[0]


# check if two packages have the same scope
def same_scope(p1, p2):
    """
    Checks if two package names have the same scope.
    
    npm allows package names to be scoped. For example, the packages '@types/lodash' and '@types/node'
    have the same scope of 'types'. This means they were published by the same author.
    """
    
    # Check if the package names are scoped
    p1_match = scope_regex.match(p1)
    p2_match = scope_regex.match(p2)

    # If either one of the package names is not scoped, then obviously
    # they do not have the same scope
    if p1_match is None or p2_match is None:
        return False

    # If both package names are scoped, check if they share the same scope
    return p1_match.group(1) == p2_match.group(1)


def repeated_characters(package_name: str, return_all: bool=False) -> List[str]:
    """
    Removes any identical consecutive characters to check for typosquatting by repeated characters.
    For example, 'reeact' could be typosquatting 'react'. Returns a list of possible typosquatting
    targets from the given popular_package_set.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.

        return_all: Whether or not to return all matches. If False, only return the most
            popular match.
    """

    # Initialize a list to hold results
    potential_typosquatting_targets = []

    # Loop through each character in the package name
    for i, c in enumerate(package_name):

        # If the next character in the given package_name is the same as the current one
        if i + 1 < len(package_name) and package_name[i + 1] == c:

            # Build a new package name by removing the duplicated character
            s = package_name[:i] + package_name[i + 1:]
    
            # If the new package name is in the list of popular packages, record it
            if s in popular_package_set and not same_scope(package_name, s) and s != package_name:
                potential_typosquatting_targets.append(s)

    # If the user has requested to return all results or there were no results
    if return_all or len(potential_typosquatting_targets) == 0:

        # simply return whatever we have
        return potential_typosquatting_targets

    # If there is at least one package and the user only wants one
    else:

        # return the most popular package
        # return in a list to match other function return styles
        return [get_most_popular_package(potential_typosquatting_targets)]
        

def omitted_chars(package_name: str, return_all: bool=False) -> List[str]:
    """
    Inserts allowed characters into file name to check for typosquatting by omission. For example,
    'evnt-stream' could be typosquatting 'event-stream'. Returns a list of potential typosquatting
    targets from the given popular_package_set.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.

        return_all: Whether or not to return all matches. If False, only return the most
            popular match.
    """

    # Initialize a list to hold results
    potential_typosquatting_targets = []

    # Do not apply this check to short package names.
    # This helps reduce the false positive rate
    if len(package_name) < 4:
        return potential_typosquatting_targets

    # Loop through every position in the given package_name
    for i in range(len(package_name) + 1):

        # Loop through every character in the list of allowed characters
        for c in allowed_characters:

            # Build a new package name by inserting the current character in the current position
            s = package_name[:i] + c + package_name[i:]

            # If the new package name is in the list of popular packages, record it
            if s in popular_package_set and not same_scope(package_name, s) and s != package_name:
                potential_typosquatting_targets.append(s)


    # If the user has requested to return all results or there were no results
    if return_all or len(potential_typosquatting_targets) == 0:

        # simply return whatever we have
        return potential_typosquatting_targets

    # If there is at least one package and the user only wants one
    else:

        # return the most popular package
        # return in a list to match other function return styles
        return [get_most_popular_package(potential_typosquatting_targets)]


def swapped_characters(package_name: str, return_all: bool=False) -> List[str]:
    """
    Swaps consecutive characters in the given package_name to search for typosquatting.
    Returns a list of potential targets from the given popular_package_set. For
    example, 'loadsh' is typosquatting 'lodash'.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.

        return_all: Whether or not to return all matches. If False, only return the most
            popular match.
    """

    # Initialize a list to hold results
    potential_typosquatting_targets = []

    # Loop through all pairs of consecutive characters in the given package_name
    for i in range(len(package_name) - 1):

        # Swap the two characters to create a new package name
        a = list(package_name)
        t = a[i]
        a[i] = a[i + 1]
        a[i + 1] = t
        s = ''.join(a)

        # If the new package name is in the list of popular packages, record it
        if s in popular_package_set and not same_scope(package_name, s) and s != package_name:
            potential_typosquatting_targets.append(s)

    # If the user has requested to return all results or there were no results
    if return_all or len(potential_typosquatting_targets) == 0:

        # simply return whatever we have
        return potential_typosquatting_targets

    # If there is at least one package and the user only wants one
    else:

        # return the most popular package
        # return in a list to match other function return styles
        return [get_most_popular_package(potential_typosquatting_targets)]


def swapped_words(package_name: str, return_all: bool=False) -> List[str]:
    """
    Reorders package_name substrings separated by delimiters to look for typosquatting.
    Also check for delimiter substitution and omission. For example, 'stream-event' and
    'event.stream' are typosquatting 'event-stream'.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.

        return_all: Whether or not to return all matches. If False, only return the most
            popular match.
    """

    # Initialize a list to hold results
    potential_typosquatting_targets = []

    # Return no targets for package names with no delimiters
    if delimiter_regex.search(package_name) is None:
        return potential_typosquatting_targets

    # Split package name on each delimiter, isolating each word
    tokens = delimiter_regex.sub(' ', package_name).split()

    # This function has factorial time complexity. To avoid
    # extremely long execution times, limit the number of tokens
    # allowed to be processed
    if len(tokens) > 8:
        return potential_typosquatting_targets

    # Get all possible permutations of the words in the package name
    for p in permutations(tokens):

        # Loop through all allowed delimiter characters
        for d in delimiters:

            # Join the words using the current delimiter to create a new package name
            s = d.join(p)

            # If the new package name is in the list of popular packages, record it
            if s in popular_package_set and not same_scope(package_name, s) and s != package_name:
                potential_typosquatting_targets.append(s)
        
    # If the user has requested to return all results or there were no results
    if return_all or len(potential_typosquatting_targets) == 0:

        # simply return whatever we have
        return potential_typosquatting_targets

    # If there is at least one package and the user only wants one
    else:

        # return the most popular package
        # return in a list to match other function return styles
        return [get_most_popular_package(potential_typosquatting_targets)]


def common_typos(package_name: str, return_all: bool=False) -> List[str]:
    """
    Applies each of the common typos to each of the characters in the given package_name.
    Checks if each result is in the list of popular package names and returns a list of
    any matches.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.

        return_all: Whether or not to return all matches. If False, only return the most
            popular match.
    """

    # Initialize a list to hold results
    potential_typosquatting_targets = []

    # Loop through all characters in the given package_name
    for i, c in enumerate(package_name):

        # Ensure the character is in the common typo dict
        if c in typos:

            # Loop through each common typo for the given character
            for t in typos[c]:

                # Build a new package name, replacing the character with the current typo character
                typo_package_name = list(package_name)
                typo_package_name[i] = t
                typo_package_name = ''.join(typo_package_name)

                # Check if the new package name is in the list of popular packages
                if typo_package_name in popular_package_set and not same_scope(package_name, typo_package_name) and typo_package_name != package_name:
                    potential_typosquatting_targets.append(typo_package_name)

    # If the user has requested to return all results or there were no results
    if return_all or len(potential_typosquatting_targets) == 0:

        # simply return whatever we have
        return potential_typosquatting_targets

    # If there is at least one package and the user only wants one
    else:

        # return the most popular package
        # return in a list to match other function return styles
        return [get_most_popular_package(potential_typosquatting_targets)]


def version_numbers(package_name: str) -> List[str]:
    """
    Checks if the given package_name adds a version number to the end of a
    popular package name. For example, 'react-2' and 'react2' could be typosquatting
    the popular package 'react'.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.
    """

    # Match the given package name on the version number regular expression
    m = version_number_regex.match(package_name)

    # If a match was found
    if m is not None:

        # Check if the match is in the list of popular packages
        s = m.group(1)
        if s in popular_package_set and not same_scope(package_name, s) and s != package_name:

            # Return the result in a list to conform with other function return types
            return [s]

    # If no match was found, simply return an empty list, showing no possible targets were found
    return []


def get_typosquatting_targets(package_name: str) -> List[str]:
    """
    Applies all typosquatting signals to the given package_name.
    Returns any potential typosquatting targets found in the given package_list.

    Arguments:
        package_name: The name of the potential typosquatting package being analyzed.
    """

    # Initialize a list used to hold possible typosquatting targets
    potential_typosquatting_targets = []

    # If the given package_name is in the given package_list, return no suspected targets
    # By our definition, a popular package cannot be typosquatting
    if package_name in popular_package_set:
        return potential_typosquatting_targets

    # Check the given package name for typosquatting
    potential_typosquatting_targets += repeated_characters(package_name)
    potential_typosquatting_targets += omitted_chars(package_name)
    potential_typosquatting_targets += swapped_characters(package_name)
    potential_typosquatting_targets += swapped_words(package_name)
    potential_typosquatting_targets += common_typos(package_name)
    potential_typosquatting_targets += version_numbers(package_name)

    # Remove any duplicate package names
    potential_typosquatting_targets = list(set(potential_typosquatting_targets))

    # Return possible targets
    return potential_typosquatting_targets


def get_all_transitive_dependencies(package_name: str) -> List[str]:
    """Returns a list of all transitive dependencies of the given package."""

    # Build the command
    command = f'node get_npm_deps_cli.js {package_name}'

    # Call the helper script, capture stdout
    output = subprocess.check_output(command).decode('utf8')
    
    # Check if the helper script could even find the given package name
    if re.search(r'could not load .* status = 404', output):
        return [package_name]

    # Convert output to a list, return result
    return output.splitlines()


def main():
    """TypoGard entry point"""

    # Check command line arguments
    if len(sys.argv) < 3:
        print('Usage: python3 typogard_npm.py [popular_package_list_filename] [package_name]')
        exit(1)
        
    # Parse command line arguments
    popular_package_list_filename = sys.argv[1]
    given_package_name = sys.argv[2]

    # Make sure the specified popular package list exists
    if not os.path.isfile(popular_package_list_filename):
        raise FileNotFoundError(f'Given popular package list filename "{popular_package_list_filename}" does not exist')

    # Read popular package list
    global popular_package_list
    popular_package_list = open(popular_package_list_filename).read().splitlines()

    # Create a set containing all popular package names for faster lookups
    global popular_package_set
    popular_package_set = set(popular_package_list)

    # Get the list of all transitive dependencies for the given package
    # These are all of the packages npm will install when the user requests given_package_name
    print(f'Fetching all transitive dependencies of {given_package_name}...')
    packages_to_be_installed = get_all_transitive_dependencies(given_package_name)
    print(f'Found {len(packages_to_be_installed) - 1} total dependencies for {given_package_name}')

    # Loop through all packages that will be installed
    print(f'Beginning typosquatting detection on {given_package_name} and its {len(packages_to_be_installed) - 1} dependencies...')
    print()
    potential_typosquatting_found = False
    for package in packages_to_be_installed:

        # Check each package for typosquatting
        potential_targets = get_typosquatting_targets(package)

        # Ignore packages with no potential typosquatting found
        if len(potential_targets) == 0:
            continue

        # Alert the user if potential typosquatting was found
        potential_typosquatting_found = True
        
        if package == given_package_name:
            print('WARNING! Package', end=' ')
        else:
            print('WARNING! Dependency', end=' ')

        print(f'{package} could be typosquatting any of these packages: {potential_targets}')
            
    # If no typosquatting was found, let the user know
    if not potential_typosquatting_found:
        print(f'No typosquatting detected for {given_package_name} or any of its dependencies')

    print()
    print('Typosquatting detection complete.')


if __name__ == '__main__':
    main()