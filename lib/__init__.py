"""
kdiff - Kubernetes Cluster Comparison Tool

A powerful command-line tool for comparing Kubernetes resources between clusters.
"""

__version__ = "1.7.5"
__author__ = "Mauro Casiraghi"
__license__ = "MIT"

# Lazy loading per ottimizzare import
__all__ = [
    "normalize",
    "compare", 
    "diff_details",
    "report",
]

def __getattr__(name):
    """Lazy import dei moduli per ridurre tempo di startup."""
    if name in __all__:
        import importlib
        module = importlib.import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
