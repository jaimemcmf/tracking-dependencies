from get_package import *
import argparse
from extools import *

parser = argparse.ArgumentParser()

parser.add_argument('-p', '--package', required=False, action='store')
parser.add_argument('-c', '--checker', required=False, action='store')
parser.add_argument('-d', '--download', required=False, action='store')

args = parser.parse_args()

if args.download is not None:
    print(args.download)
    prev_down = set()
    prev_down.add(args.download)
    cur = download_package(args.download)
    deps = find_deps(cur)
    while True:
        if not deps:
            break
        else:
            for dep in deps:
                deps.remove(dep)
                if type(dep) is list:
                    dep = dep[0]
                    
                dep = parse_package_name(dep)[0]
                
                if dep in prev_down or dep is None:
                    continue
                else:
                    prev_down.add(str(dep))
                
                print(dep)
                prev_down.add(dep)
                cur = download_package(dep)
                ndeps = find_deps(cur)
                if ndeps:
                    deps.append(ndeps)
                    deps = flatten(deps)


if args.package is None and args.download is None:
    iter_pypi()
#else:
    #print(args.package)
    #get_all_deps(args.package, '    ')
    