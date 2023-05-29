import pkg_resources
import re
from standard_library import *

def get_dependencies_with_semver_string(package_name):
    package = pkg_resources.working_set.by_key[package_name]
    return [str(r) for r in package.requires()]

def recursive_deps(dependencies, spacing):
    if dependencies == []: return
    for package in dependencies:
        print(spacing + package)
        dep_name = parse_package_name(package)
        try: new_dependencies = get_dependencies_with_semver_string(dep_name)
        except: new_dependencies = []
        recursive_deps(new_dependencies, spacing+"   ")

def parse_package_name(dependency):     
    return re.split('<|>|!|=', dependency)[0]

_package_name = input()
try: dependencies = get_dependencies_with_semver_string(_package_name)
except: dependencies = "Package not found."

if type(dependencies) != str: recursive_deps(dependencies, "")
else: print(dependencies)