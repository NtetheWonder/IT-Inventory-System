"""Data package for Excel storage and data utilities.

Exports the primary data module for convenient imports:

from data import excel_store

Use `from data import excel_store` or `from data.excel_store import <symbol>`.
"""

from . import excel_store

__all__ = ["excel_store"]
