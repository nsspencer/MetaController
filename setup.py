from setuptools import find_packages, setup

setup(
    name="metacontroller",
    version="0.1.1",
    author="Nathan Spencer",
    author_email="nathanss1997@gmail.com",
    description="A Python library for decoupling logic, modeling dynamic systems, and writing more declarative software.",
    long_description_content_type="text/markdown",
    url="https://github.com/nsspencer/MetaController",
    license="BSD 3-Clause",
    python_requires=">=3.8",
    packages=find_packages(exclude=["test"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
    install_requires=[],  # no dependencies!
)
