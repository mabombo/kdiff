"""
kdiff - Kubernetes Cluster Comparison Tool

A powerful command-line tool for comparing Kubernetes resources between clusters.
"""

__version__ = "1.0.0"
__author__ = "Mauro Casiraghi"
__license__ = "MIT"

# Esporta moduli principali
from . import normalize
from . import compare
from . import diff_details
from . import report
from . import report_md

__all__ = [
    "normalize",
    "compare", 
    "diff_details",
    "report",
    "report_md",
]
