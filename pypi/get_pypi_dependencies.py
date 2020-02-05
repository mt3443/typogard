import requests
import sys

def get_dependencies(package):
    dependencies = set()
    todo = [package]

    while len(todo) != 0:
        package_name = todo.pop(0)

        r = requests.get('https://pypi.org/pypi/{}/json'.format(package_name))

        if r.status_code != 200:
            print('Metadata request for {} returned status code {}'.format(package_name, r.status_code))
        else:
            try:
                metadata = r.json()
                deps = metadata['info']['requires_dist']

                if deps is None:
                    continue

                for d in deps:
                    d_name = d.split()[0]

                    if d_name[-1] == ';':
                        d_name = d_name[:-1]
                    
                    if d_name not in dependencies:
                        dependencies.add(d_name)
                        todo.append(d_name)

            except:
                print('Unhandled exception when processing {}'.format(package_name))

    return list(dependencies)


def main():
    if len(sys.argv) != 2:
        print('usage: py get_pypi_dependencies.py [package_name]')
        exit(1)

    print(get_dependencies(sys.argv[1]))


if __name__ == '__main__':
    main()