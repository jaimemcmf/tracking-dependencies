from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import os

path_to_project = '/Users/jaimemcmf/Documents/Ciência de Computadores — FCUP/3rd Year/2nd Semester/Projeto/downloaded_pkgs/'

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
    
