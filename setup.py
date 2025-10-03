"""Setup configuration for Commercial-View."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="commercial-view",
    version="1.0.0",
    author="Commercial-View Team",
    description="Portfolio monitoring and optimization framework for commercial lending",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeninefer/Commercial-View",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "gdrive": [
            "google-auth>=2.23.0",
            "google-auth-oauthlib>=1.1.0",
            "google-auth-httplib2>=0.1.1",
            "google-api-python-client>=2.100.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json"],
    },
)
