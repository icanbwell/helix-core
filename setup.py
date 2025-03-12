# noinspection Mypy
from typing import Any

from setuptools import setup, find_packages
from os import path, getcwd

# from https://packaging.python.org/tutorials/packaging-projects/

# noinspection SpellCheckingInspection
package_name = "helixcore"

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    with open(path.join(getcwd(), "VERSION")) as version_file:
        version = version_file.read().strip()
except IOError:
    raise


def fix_setuptools() -> None:
    """Work around bugs in setuptools.

    Some versions of setuptools are broken and raise SandboxViolation for normal
    operations in a virtualenv. We therefore disable the sandbox to avoid these
    issues.
    """
    try:
        from setuptools.sandbox import DirectorySandbox

        # noinspection PyUnusedLocal
        def violation(operation: Any, *args: Any, **_: Any) -> None:
            print("SandboxViolation: %s" % (args,))

        DirectorySandbox._violation = violation
    except ImportError:
        pass


# Fix bugs in setuptools.
fix_setuptools()


# classifiers list is here: https://pypi.org/classifiers/

# create the package setup
setup(
    name=package_name,
    version=version,
    author="Imran",
    author_email="imran.qureshi@icanbwell.com",
    description="helixcore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/icanbwell/helix-core",
    packages=find_packages(),
    install_requires=[
        "fhir.resources<8,>=7.1.0",
        "dataclasses-json>=0.6.7",
        "boto3>=1.34.140",
        "helix.fhir.client.sdk>=3.0.27",
        "furl>=2.1.3",
        "mlflow-skinny>=2.17.2",
        "sqlparse>=0.5.3",
        "pymysql>=1.1.1",
        "aiomysql>=0.2.0",
        "aiohttp>=3.11.13",
        "structlog>=23.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    dependency_links=[],
    include_package_data=True,
    zip_safe=False,
    package_data={"helixcore": ["py.typed"]},
)
