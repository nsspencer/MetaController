from setuptools import find_packages, setup

setup(
    name="pycontroller",
    version="0.1.1",
    author="Nathan Spencer",
    author_email="nathanss1997@gmail.com",
    description="A Python library for modeling dynamic systems.",
    long_description_content_type="text/markdown",
    url="https://github.com/nsspencer/ControllerPy",
    packages=find_packages(exclude=["test"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "test": ["pytest ~= 7.0", "coverage ~= 6.0", "black >= 21.8b"],
    },
    zip_safe=True,
    install_requires=[],  # no dependencies!
)
