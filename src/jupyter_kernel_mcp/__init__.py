"""
Jupyter Kernel MCP Server

A Model Context Protocol (MCP) server for stateful Jupyter kernel development.
Provides multi-kernel support for AI agents and assistants.
"""

from .server import main

__version__ = "0.1.0"
__all__ = ["main"]