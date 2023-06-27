"""main file rn"""
import os
import re
import sys
import pickle

from configparser import ConfigParser
import string
from pip._vendor import tomli

from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

from extools import *

path_to_source = os.getcwd() + '/'
path_to_downloaded = os.path.dirname(os.getcwd())+'/downloaded_packages/'
path_to_root = os.path.dirname(os.getcwd()) + '/'


def download_package(pkg):
    """searches, downloads and decompresses the input package from PyPI Simple API"""
    packages = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    driver.get("https://pypi.org/simple/" + pkg + "/")

    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    packages = soup.findAll('a')

    try:
        while ".tar.gz" not in str(packages[-1]):
            packages.pop()
        to_down = str(packages[-1])
    except:
        return None

    to_down = to_down.split('href="', 1)[1]
    url = to_down.split('">', 1)[0]
    name = to_down.split('">', 1)[1].split("</a>")[0]

    try:
        request = requests.get(url, timeout=10)
    except TimeoutError:
        return None
    
    with open(path_to_downloaded + name, 'wb') as file:    
        file.write(request.content)
    wdir = os.getcwd()
    os.chdir(path_to_downloaded)
    os.system("tar -xzf " + name)
    os.system("rm " + name)
    os.chdir(wdir)
    
    return name.split('.tar.gz')[0]

def get_pypi_packages():
    
    if not os.path.isfile('pypi_packages.txt'):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        driver.get("https://pypi.org/simple/")

        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")
        print("Getting packages names from PyPI. This may take a while...")
        packages = soup.findAll('a')
        out = []
        for pkg in packages:
            pkg = str(pkg)
            pkg = pkg.split('>',1)[1]
            pkg = pkg.split('<',1)[0]
            out.append(pkg)
        
        with open('pypi_packages.txt', 'a') as f:
            for pkg in out:
                print(pkg, file=f)

    packages = []
    with open('pypi_packages.txt', 'r') as f:
        pkgs = f.readlines()
        for pkg in pkgs:
            pkg = pkg.split('\n',1)[0]
            packages.append(pkg)

    return packages


    
#returns list of raw dependency names
def find_deps(pkg):
    """search for dependencies in a project"""

    dependencies = []

    try:
        os.chdir(path_to_downloaded + pkg)
    except:
        return dependencies

    has_pyproject = os.path.isfile("pyproject.toml")
    has_setuppy = os.path.isfile("setup.py")
    has_metadata = os.path.isfile("METADATA")
    has_setupcfg = os.path.isfile("setup.cfg")

    if not has_pyproject and not has_setuppy and not has_metadata and not has_setupcfg:
        return []

    if has_pyproject:
        with open("pyproject.toml", encoding="utf-8") as file:
            pp_toml = tomli.loads(file.read())
        project = pp_toml.get("project")
    else: project = None
    if project is not None:
        if "dependencies" not in project:
            return []
        dependencies = dependencies + project["dependencies"]

    #finding dependencies in setup.py file
    if has_setuppy:
        deps = []
        with open('setup.py', 'r', encoding="utf-8") as file:
            content = file.read()
        if "setup" in content and "install_requires" in content:
            try:
                content = content.translate({ord(c): None for c in string.whitespace})
                content = content.split("install_requires=[")[1]
                content = content.split("]",1)[0]
                raw_deps = content.split(',')
                raw_deps.pop()
                for dep in raw_deps:
                    dep = dep[1:]
                    dep = dep[:-1]
                    deps.append(dep)
            except:
                pass
            dependencies = dependencies + deps

    #finding dependencies in METADATA file
    if has_metadata:
        with open("METADATA", 'r+', encoding="utf-8") as file:
            content = file.readlines()
            for line in content:
                if 'Requires-Dist:' in line:
                    dependencies = dependencies.append(line.split(' ', 1))[1]

    #finding dependencies in setup.cfg file
    if has_setupcfg:
        parser = ConfigParser()
        parser.read("setup.cfg")
        try:
            reqs = parser['options']['install_requires'].split('\n')
            if reqs[0] == "":
                reqs.pop(0)
            dependencies = dependencies + reqs
        except:
            pass
        
    os.chdir(path_to_downloaded)
    return dependencies

def find_hardcoded_urls(file):
    with open(file, 'r', encoding="utf-8") as file:
        content = file.read()
        
        hardcoded_urls = re.search('https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)', content)
        if hardcoded_urls is not None:
            return True
        
    return False


def scan(pkg):
    
    try:
        os.chdir(path_to_downloaded + pkg)
    except:
        os.chdir(path_to_downloaded) 
        return False
    
    if not os.path.isfile("setup.py"):
        return False
    
    try:
        cleanfile = remove_comments(path_to_downloaded + pkg, 'setup.py')
    except:
        cleanfile = remove_comments(path_to_downloaded, 'setup.py')
    
    try:
        if find_hardcoded_urls(cleanfile) and not url_in_setup(cleanfile) and not url_in_prints(cleanfile):
            return True
        
        if manual_pip_install(cleanfile):
            return True
    except:
        os.chdir(path_to_downloaded) 
        return False    
    
    os.chdir(path_to_downloaded) 
    return False   

    
def parse_package_name(dependency):
    """
    used for creating a tuple for the function name
    example: numpy>2.0 => (numpy,>,2.0)
    useful for downloading the exact package version (not implemented)
    """
    dependency = re.split(';', dependency)[0]
    try:
        operation = re.search("(>=|<=|<|>|==)", dependency).group()
    except:
        operation = None
    spl = re.split('>=|<=|<|>|==', dependency)
    if operation is None:
        version = None
    else:
        try:
            version = spl[1]
        except:
            version = None
    if operation is not None:
        operation.strip()
        version.strip()

    return (spl[0].strip(), operation, version)


def get_all_deps(pkg, ident):
    """
    recursively search for dependencies and build a tree
    also analyze
    """
    os.chdir(path_to_downloaded)
    try:
        if pkg not in visited:
            
            visited.add(str(pkg))
            pkg_name = download_package(pkg)
            new_deps = find_deps(pkg_name)
        
            if scan(pkg_name):
                print(f'{Fore.RED}{ident}Potentially malicious package found: {pkg_name}{Style.RESET_ALL}')
                os.chdir(path_to_downloaded)
                os.system('mv ' + pkg_name + " " + path_to_root+"flagged_packages/")
            else:
                os.system('rm -drf ' + str(pkg_name))
            
            for dep in new_deps:
                dep = parse_package_name(dep)[0]
                print(ident+dep)
                get_all_deps(dep, ident+"   ")
                
    except NameError:
            pkg_name = download_package(pkg)
            new_deps = find_deps(pkg_name)

            if scan(pkg_name):
                print(f'{Fore.RED}{ident}Potentially malicious package found: {pkg_name}{Style.RESET_ALL}')
                os.system('mv ' + pkg_name + " " + path_to_root+"flagged_packages/")
            else:
                try: 
                    os.system('rm -drf ' + str(pkg_name))
                except Exception as e:
                    print('Package <' + pkg_name + '>', e)
            
            for dep in new_deps:
                dep = parse_package_name(dep)[0]
                print(ident+dep)
                get_all_deps(dep, ident+"   ")


def iterate_pypi():
    global visited
    visited = set()
    
    packages = get_pypi_packages()
    if os.path.isfile(path_to_source + '/last_visited.txt'):
        choice = input('Do you wish to continue from last iteration? [y/n]')
        if choice == 'y':
            with open(path_to_source + '/last_visited.txt', 'rb') as file:
                visited = pickle.load(file)
    
    for pkg in packages:
        try:
            print(pkg)
            get_all_deps(pkg, "     ")
        except KeyboardInterrupt:
            os.chdir(path_to_source)
            save_visited(visited)
            sys.exit()