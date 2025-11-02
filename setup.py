"""
AidMind - Unsupervised machine learning for humanitarian needs assessment
"""
from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aidmind",
    version="1.0.1",
    author="AidMind Team",
    author_email="support@aidmind.org",
    description="Unsupervised machine learning for humanitarian needs assessment and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/aidmind",
    project_urls={
        "Bug Tracker": "https://github.com/yourorg/aidmind/issues",
        "Documentation": "https://github.com/yourorg/aidmind#readme",
        "Source Code": "https://github.com/yourorg/aidmind",
    },
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    py_modules=["aidmind"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Sociology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "notebook": [
            "jupyter>=1.0",
            "notebook>=6.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "aidmind=aidmind:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
    keywords=[
        "humanitarian",
        "needs assessment",
        "machine learning",
        "clustering",
        "geospatial",
        "visualization",
        "aid",
        "NGO",
        "international development",
    ],
    zip_safe=False,
)
