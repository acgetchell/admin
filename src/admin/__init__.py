"""
Admin module for basic system administration tasks.

This module provides core functionality for admin operations.
"""

__version__ = '0.1.0'
__author__ = 'Adam Getchell'


def main() -> None:
    """Execute the main admin function.

    Prints welcome message and version information.
    """
    print(f"Admin Module v{__version__}")
    print("Hello from admin!")


# Package exports
__all__ = ['main']
