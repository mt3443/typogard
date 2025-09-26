# TypoGard
TypoGard is a client-side tool created to protect users from [package typosquatting attacks](https://snyk.io/blog/typosquatting-attacks/). TypoGard was originally implemented as a standalone tool for npm, but it can easily be extended to other languages and can even be embedded in package installation software.

## How TypoGard Works
TypoGard works by applying a number of transformations to a given package name and comparing the results to a list of popular package names. These transformations are based on the same transformations made by malicious actors in past package typosquatting attacks. For more detailed information, read the [TypoGard paper on arXiv](https://arxiv.org/abs/2003.03471) (the tool was referred to as SpellBound at the time of publication).

## TypoGard Requirements
The version of TypoGard in this repository, which specifically targets npm, relies on the following:
* [Python3](https://www.python.org/downloads/) (tested with Python 3.9.4, but other versions may work too)
* [Node.js](https://nodejs.org/en/) (with version 16.13.0, but other versions may work too)
* [npm-remote-ls](https://www.npmjs.com/package/npm-remote-ls) (an npm package that lists npm package dependencies. The exact version of this package and all dependencies can be found in package-lock.json)

## TypoGard Usage

`python3 typogard_npm.py [popular_package_list_filename] [package_name]`

TypoGard fundementally relies on a list of packages considered to be popular. Users can specify this list, which contains a different popular package name on each line, through the `popular_package_list_filename` command line argument. A sample file, `popular_npm_packages_sample.txt`, containing the top ~1% of popular npm packages based on total downloads has been included in this repository.
The `package_name` argument is used to specify which package (along with all, if any, of its transitive dependencies) should be checked for typosquatting.

### Example Usage:

If one would like to determine whether the theoretical package `event_stream` is typosquatting any popular packages, they could use:

`python3 typogard_npm.py popular_npm_packages_sample.txt event_stream`

This will notify the user that `event_stream` could be typosquatting the popular package `event-stream`.

## Integration with npm

We have included a proof-of-concept modified version of the npm package installer which runs TypoGard prior to installation. You can find it under _paper/npm/modified_installer.zip_.
