if (process.argv[2] == undefined) {
    console.log('Usage: node get_npm_deps_cli.js [package_name]');
    process.exit(1);
}

var ls = require('npm-remote-ls').ls;
var config = require('npm-remote-ls').config;

config({
    development: false
});

package_name = process.argv[2];

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

    return Array.from(temp_set);
}

ls(package_name, 'latest', true, (r) => {
    let dependencies = clean_deps(r);
    console.log('Dependencies:')
    for (let dependency of dependencies) {
        console.log(dependency);
    }
});