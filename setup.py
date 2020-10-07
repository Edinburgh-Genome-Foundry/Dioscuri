from setuptools import setup, find_packages

version = {}
with open("dioscuri/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="dioscuri",
    version=version["__version__"],
    author="Peter Vegh",
    description="Read/write Gemini WorkList (gwl) files.",
    long_description=open("pypi-readme.rst").read(),
    license="MIT",
    url="https://github.com/Edinburgh-Genome-Foundry/Dioscuri",
    keywords="biology",
    packages=find_packages(exclude="docs"),
)
