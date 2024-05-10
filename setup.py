from setuptools import find_packages, setup

setup(
    name="pycontroller",
    version="0.0.1",
    author="Nathan Spencer",
    author_email="nathanss1997@gmail.com",
    description="A Python library for managing controlled logic.",
    long_description_content_type="text/markdown",
    url="https://github.com/nsspencer/ControllerPy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
)
