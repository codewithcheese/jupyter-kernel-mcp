"""
Jupyter Kernel MCP Server

A Model Context Protocol (MCP) server for stateful Jupyter kernel development.
Provides multi-language support (Python, TypeScript, JavaScript) for AI agents and assistants.
"""

from .server import main

__version__ = "0.2.0"
__all__ = ["main"]