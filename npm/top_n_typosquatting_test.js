var typosquatting = require('./typosquatting');
var fs = require('fs');
var csvjson = require('csvjson');
var ls = require('npm-remote-ls').ls;
var config = require('npm-remote-ls').config;

const num_to_download = 1000;

var all_packages_json = csvjson.toObject(fs.readFileSync('../data/npm_download_counts.csv').toString());
var all_packages = [];
for (let p of all_packages_json) {
    all_packages.push(p.package_name);
}
delete all_packages_json;

config({
    development: false
});

function get_packages_to_be_installed(dependency_tree) {
    
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

var counter = 0;

function scan() {
    let package_name = all_packages.shift();
    console.log(counter);
    ls(package_name, 'latest', true, (r) => {
        var packages_to_be_installed = get_packages_to_be_installed(r);

        for (let p of packages_to_be_installed) {
            let results = typosquatting.scan_package(p);

            if (results != null) {
                console.log(package_name);
            }
        }
        
        // move on to the next package
        counter++;
        if (counter < num_to_download) {
            scan()
        }
    });
}

scan();