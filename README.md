
<h1> Finding PyPI dependencies and static code analysis </h1>

This project was developed in the scope of the course Internship/Project for the bachelor's in Computer Science at Faculdade de Ciências da Universidade do Porto (FCUP).

<h2> Motivation and Goals
</h2>
The motivation for this project was the common attack through malicious packages submitted to PyPI.
It was found that the commonly used setup.py file is executed both in

    $ pip install package_name
and

    $ pip download package_name

and is the file that usually contains the malicious code.

The final goal of this project was to build a tool capable of finding every dependency of a package and check for the presence of common attacks. All this **without executing** any package's code.

<h2> How to execute
</h2>

The main.py file is the file to be executed.
Simply using 

    $ python main.py

will iterate a file (pypi_packages.txt) containing all PyPI packages and perform the dependency search and code analysis on each. If this file does not yet exist, it will be created. This process may take close to **5 minutes**.

<h3>Flags</h3>

\
**-p / --package**

Performs the dependency search and static code analysis on only one package.

    $ python main.py -p package_name

\
**-d / --download**

Does a similar job to pip download command, without executing any files. The downloaded packages can be found in the "downloaded_packages" directory.
    
    $ python main.py -d package_name

\
**-c / --checker**

Receives a Python file (must be present in the "checker" directory) and performs the static code analysis on it.

    $ python main.py -c file.py
