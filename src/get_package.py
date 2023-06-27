"""main file rn"""
import os
import re
import sys
import pickle

from configparser import ConfigParser
import string
from pip._vendor import tomli


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

from extools import *
from searchindex import get_pypi_packages

path_to_project = '/Users/jaimemcmf/Documents/University/Ciência de Computadores — FCUP/3rd Year/2nd Semester/Projeto/searching_pypi_deps/downloaded_pkgs/'
path_to_source = '/Users/jaimemcmf/Documents/University/Ciência de Computadores — FCUP/3rd Year/2nd Semester/Projeto/searching_pypi_deps/src/'

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
    
    with open(path_to_project + name, 'wb') as file:    
        file.write(request.content)
    wdir = os.getcwd()
    os.chdir(path_to_project)
    os.system("tar -xzf " + name)
    os.system("rm " + name)
    os.chdir(wdir)
    
    return name.split('.tar.gz')[0]


    
#returns list of raw dependency names
def find_deps(pkg):
    """search for dependencies in a project"""

    dependencies = []

    try:
        os.chdir(path_to_project + pkg)
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
        
    os.chdir(path_to_project)
    return dependencies

def find_hardcoded_urls():
    with open('clean_setup.py', 'r', encoding="utf-8") as file:
        content = file.read()
        if 'http://' in content or 'https//' in content:
            return True
    return False

            

def scan(pkg):
    is_suspicious = False
    try:
        os.chdir(path_to_project + pkg)
    except:
        os.chdir(path_to_project) 
        return False
    
    has_setuppy = os.path.isfile("setup.py")

    if not has_setuppy:
        return False
    
    remove_comments()
    try:
        if find_hardcoded_urls() and not url_in_setup() and not url_in_prints():
            is_suspicious = True
        
        if manual_pip_install():
            is_suspicious = True
    except:
        os.chdir(path_to_project) 
        return False    
    

    os.chdir(path_to_project) 
    return is_suspicious    

    
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
    os.chdir(path_to_project)
    
    try: visited
    except NameError:
        visited = set()
    
    if pkg not in visited:
        
        visited.add(str(pkg))
        pkg_name = download_package(pkg)
        new_deps = find_deps(pkg_name)
    
        if scan(pkg_name):
            print("Potentially malicious package found -> " + pkg_name)
            os.system('mv ' + pkg_name + " ../flagged_packages")
        else:
            try: 
                os.system('rm -drf ' + str(pkg_name))
            except Exception as e:
                print('Package <' + pkg_name + '>', e)
        
        for dep in new_deps:
            dep = parse_package_name(dep)[0]
            print(ident+dep)
            get_all_deps(dep, ident+"   ")


def iter_pypi():
    global visited
    visited = set()
    
    packages = get_pypi_packages()
    if os.path.isfile(path_to_source + '/last_visited.txt'):
        print('Do you wish to continue from last iteration?')
        choice = input()
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
        


if __name__ == "__main__":
    iter_pypi()