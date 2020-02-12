var fs = require('fs');
var typosquatting = require('./typosquatting');

// Get sample, read package names
var packages = fs.readFileSync('../data/npm_sample').toString().split('\r\n');

// Open output log file
var log = fs.openSync('../data/npm_sample_results', 'a');

// Ignore devDependencies
config({
    development: false
});

function clean_deps(dependency_tree) {
    
    let temp_set = new Set();

    for (let package of dependency_tree) {

        // remove version number
        let package_name = null;
        if (package[0] == '@') {
            let at_index = package.indexOf('@', 1);
            package_name = package.substring(0, at_index);
        } else {
            package_name = package.split('@')[0];
        }

        // add package name to set
        temp_set.add(package_name);

    }

    return temp_set;
}

function scan() {
    let package = packages.shift();
    ls(package, 'latest', true, (r) => {

        let packages_to_scan = clean_deps(r);
        let alert = false;

        for (let p of packages_to_scan) {
            let result = typosquatting.scan_package(p);

            if (result != null) {
                fs.writeFileSync(log, p + ',yes\n');
                alert = true;
                break;
            }
        }

        if (alert == false) {
            fs.writeFileSync(log, package + ',no\n');
        }

        if (packages.length != 0) {
            scan();
        }

    });
}

scan();