#import pathlib
from setuptools import setup

## The directory containing this file
#HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sfphase_pimc_tools",
    version="1.0.0",
    description="Three modules for analyzing phase diagram",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/skim30-uvm",
    author="Sang Wook Kim",
    author_email="skim30@uvm.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["phase_tools"],
    install_requires=["numpy", "pandas", "scipy", "graphenetools-py", "erroranalysis-py", "matplotlib"],
    entry_points={
        "console_scripts": [
            "phase_tools=phase_tools.__main__:main",
        ]
    },
)
