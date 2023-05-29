import distutils.command.build_py
from distutils.command.clean import clean
import subprocess  
from shutil import copytree, rmtree
from os import environ, path
from sys import argv, exit  
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand
class PreInstallCommand(distutils.command.build_py.build_py):
    description = "Pull in the schemas that live in the TypeScript package."
    def run(self):
        pkgdir = path.dirname(path.realpath(argv[0]))
        rmtree(
            path.join(pkgdir, "src", "zero_ex", "json_schemas", "schemas"),
            ignore_errors=True,
        )
        copytree(
            path.join(
                pkgdir, "..", "..", "packages", "json-schemas", "schemas"
            ),
            path.join(pkgdir, "src", "zero_ex", "json_schemas", "schemas"),
        )
class TestCommandExtension(TestCommand):
    def run_tests(self):
        import pytest
        exit(pytest.main(["--doctest-modules", "-rapP"]))
class LintCommand(distutils.command.build_py.build_py):
    description = "Run linters"
    def run(self):
        lint_commands = [
            "black --line-length 79 --check --diff src test setup.py".split(),
            "pycodestyle src test setup.py".split(),
            "pydocstyle src test setup.py".split(),
            "mypy src test setup.py".split(),
            "bandit -r src ./setup.py".split(),
            "pylint src test setup.py".split(),
        ]
        environ["MYPYPATH"] = path.join(
            path.dirname(path.realpath(argv[0])), "stubs"
        )
        for lint_command in lint_commands:
            print(
                "Running lint command `", " ".join(lint_command).strip(), "`"
            )
            subprocess.check_call(lint_command)  
class CleanCommandExtension(clean):
    def run(self):
        super().run()
        rmtree("build", ignore_errors=True)
        rmtree("dist", ignore_errors=True)
        rmtree(".mypy_cache", ignore_errors=True)
        rmtree(".tox", ignore_errors=True)
        rmtree(".pytest_cache", ignore_errors=True)
        rmtree("src/0x_json_schemas.egg-info", ignore_errors=True)
class TestPublishCommand(distutils.command.build_py.build_py):
    description = (
        "Publish dist/* to test.pypi.org. Run sdist & bdist_wheel first."
    )
    def run(self):
        subprocess.check_call(  
            (
                "twine upload --repository-url https://test.pypi.org/legacy/"
                + " --verbose dist/*"
            ).split()
        )
class PublishCommand(distutils.command.build_py.build_py):
    description = "Publish dist/* to pypi.org. Run sdist & bdist_wheel first."
    def run(self):
        subprocess.check_call("twine upload dist/*".split())  
class PublishDocsCommand(distutils.command.build_py.build_py):
    description = (
        "Publish docs to "
        + "http://0x-json-schemas-py.s3-website-us-east-1.amazonaws.com/"
    )
    def run(self):
        subprocess.check_call("discharge deploy".split())  
with open("README.md", "r") as file_handle:
    README_MD = file_handle.read()
setup(
    name="0x-json-schemas",
    version="2.1.0",
    description="JSON schemas for 0x applications",
    long_description=README_MD,
    long_description_content_type="text/markdown",
    url=(
        "https://github.com/0xProject/0x-monorepo/tree/development"
        + "/python-packages/json_schemas"
    ),
    author="F. Eugene Aumson",
    author_email="feuGeneA@users.noreply.github.com",
    cmdclass={
        "pre_install": PreInstallCommand,
        "clean": CleanCommandExtension,
        "lint": LintCommand,
        "test": TestCommandExtension,
        "test_publish": TestPublishCommand,
        "publish": PublishCommand,
        "publish_docs": PublishDocsCommand,
    },
    install_requires=["jsonschema", "mypy_extensions", "stringcase"],
    extras_require={
        "dev": [
            "0x-contract-addresses",
            "bandit",
            "black",
            "coverage",
            "coveralls",
            "eth_utils",
            "mypy",
            "mypy_extensions",
            "pycodestyle",
            "pydocstyle",
            "pylint",
            "pytest",
            "sphinx",
            "sphinx-autodoc-typehints",
            "tox",
            "twine",
        ]
    },
    python_requires=">=3.6, <4",
    package_data={"zero_ex.json_schemas": ["py.typed", "schemas/*"]},
    package_dir={"": "src"},
    license="Apache 2.0",
    keywords=(
        "ethereum cryptocurrency 0x decentralized blockchain dex exchange"
    ),
    namespace_packages=["zero_ex"],
    packages=find_packages("src"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
        "Topic :: Other/Nonlisted Topic",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    zip_safe=False,  
    command_options={
        "build_sphinx": {
            "source_dir": ("setup.py", "src"),
            "build_dir": ("setup.py", "build/docs"),
            "warning_is_error": ("setup.py", "true"),
        }
    },
)