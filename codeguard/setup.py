"""
CodeGuard - Code Plagiarism Detection System
Setup configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="codeguard",
    version="1.0.0",
    description="Code plagiarism detection system for Python source code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael Andrew Devlyn Roach, Roberto Castro Soto",
    author_email="a01781041@tec.mx",
    url="https://github.com/yourusername/codeguard",
    license="MIT",

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Python version requirement
    python_requires=">=3.11",

    # Dependencies
    install_requires=[
        "Flask>=3.0.0",
    ],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
            "pylint>=2.17.5",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "pytest-benchmark>=4.0.0",
        ],
    },

    # Entry points
    entry_points={
        "console_scripts": [
            "codeguard=src.web.app:main",
        ],
    },

    # Package data
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],

    # Keywords
    keywords="plagiarism detection code analysis education academic-integrity",

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/codeguard/issues",
        "Source": "https://github.com/yourusername/codeguard",
        "Documentation": "https://github.com/yourusername/codeguard/docs",
    },
)
