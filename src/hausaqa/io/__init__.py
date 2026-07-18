"""Thin input adapters for bilingual localization files."""

from .delimited import read_delimited
from .json_pairs import read_json_pairs
from .xliff import read_xliff

__all__ = ["read_delimited", "read_json_pairs", "read_xliff"]
