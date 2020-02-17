var ls = require('npm-remote-ls').ls;
var config = require('npm-remote-ls').config;
var fs = require('fs');

var node_name = process.argv[2];

// get the names of packages assigned to this node
var todo_packages = fs.readFileSync('/users/m139t745/typosquatting/npm/npm_dependencies/' + node_name).toString().split(/\s+/);

// output file
var output_stream = fs.createWriteStream('/volatile/m139t745/npm_dependencies/' + node_name, {'flags': 'a'})

// turn of dev dependencies
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

        // this package has 0 dependents and 0 dependencies, causes many problems in nodejs
        if (package_name == 'null') {
            continue
        }

        // add package name to set
        temp_set.add(package_name);

    }

    return Array.from(temp_set);
}

function make_call() {

    let current_package = todo_packages.shift();

    if (todo_packages.length % 1000 == 0) {
        console.log(todo_packages.length);
    }

    ls(current_package, 'latest', true, (r) => {

        let dependencies = get_packages_to_be_installed(r);
        let output_string = current_package;

        for (let dependency of dependencies) {
            output_string += (',' + dependency);
        }

        output_stream.write(output_string + '\n');

        if (todo_packages.length != 0) {
            make_call();
        }
    });
}

make_call();