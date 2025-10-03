"""
Setup configuration for Commercial-View package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="commercial-view",
    version="0.1.0",
    author="Commercial View Team",
    description="Principal KPI analytics for commercial loan portfolios",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
