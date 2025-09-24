from setuptools import setup, find_packages

setup(
    name="dab_py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",  # for HTTP requests to the DAB API
    ],
    license="GPL-3.0",
    author="Ahmad Mahmoud (CNR internship)",
    description="A Python client for interacting with the DAB API.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ESSI-Lab/dab-py/tree/main",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)