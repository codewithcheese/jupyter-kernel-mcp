#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Jupyter Kernel MCP tests
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Set up test environment"""
    # Ensure we're in test mode
    os.environ['JUPYTER_KERNEL_MCP_TEST'] = 'true'
    
    yield
    
    # Clean up
    if 'JUPYTER_KERNEL_MCP_TEST' in os.environ:
        del os.environ['JUPYTER_KERNEL_MCP_TEST']


@pytest.fixture
def python_executable():
    """Provide current Python executable path"""
    return sys.executable


@pytest.fixture(autouse=True)
def clean_kernels():
    """Ensure clean kernel state for each test"""
    from jupyter_kernel_mcp.server import kernels, shutdown_kernel
    
    # Clean up before test
    kernel_ids = list(kernels.keys())
    for kid in kernel_ids:
        try:
            shutdown_kernel(kid)
        except:
            pass
    kernels.clear()
    
    yield
    
    # Clean up after test  
    kernel_ids = list(kernels.keys())
    for kid in kernel_ids:
        try:
            shutdown_kernel(kid)
        except:
            pass
    kernels.clear()