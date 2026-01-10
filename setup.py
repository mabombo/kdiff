#!/usr/bin/env python3
"""
Setup script for kdiff - Kubernetes Cluster Comparison Tool
"""
from setuptools import setup, find_packages
from pathlib import Path

# Leggi README per long_description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="kdiff",
    version="1.5.3",
    description="Kubernetes cluster comparison tool with intelligent diff detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mauro Casiraghi",
    author_email="",
    url="https://github.com/maurocasiraghi/kdiff",
    license="MIT",
    
    # Pacchetti Python da installare
    packages=['lib'],
    
    # Script eseguibile
    scripts=["bin/kdiff"],
    
    # Requisiti Python
    python_requires=">=3.10",
    
    # Nessuna dipendenza esterna (solo stdlib)
    install_requires=[],
    
    # Dipendenze opzionali per sviluppo
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ]
    },
    
    # Classificatori PyPI
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    
    # Keywords per ricerca PyPI
    keywords=[
        "kubernetes",
        "k8s",
        "diff",
        "comparison",
        "devops",
        "cluster",
        "kubectl",
        "deployment",
        "infrastructure",
    ],
    
    # Metadati progetto
    project_urls={
        "Bug Reports": "https://github.com/mabombo/kdiff/issues",
        "Source": "https://github.com/mabombo/kdiff",
        "Documentation": "https://github.com/mabombo/kdiff/blob/main/README.md",
    },
)
