#!/usr/bin/env python3
"""
Test suite for Jupyter Kernel MCP Server
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jupyter_kernel_mcp.server import (
    create_kernel, shutdown_kernel, execute_code_in_kernel, 
    get_kernel_client, kernels
)


class TestKernelManagement:
    """Test kernel lifecycle management"""
    
    def setup_method(self):
        """Clear kernels before each test"""
        # Clear any existing kernels
        kernel_ids = list(kernels.keys())
        for kid in kernel_ids:
            try:
                shutdown_kernel(kid)
            except:
                pass
        kernels.clear()
    
    def teardown_method(self):
        """Clean up after each test"""
        self.setup_method()
    
    def test_kernel_creation_with_valid_python(self):
        """Test creating a kernel with current Python executable"""
        python_path = sys.executable
        
        kernel_id = create_kernel(python_path, "test-kernel")
        
        assert kernel_id == "test-kernel"
        assert kernel_id in kernels
        assert kernels[kernel_id]['python_env'] == python_path
        
        # Clean up
        shutdown_kernel(kernel_id)
    
    def test_kernel_creation_with_invalid_python(self):
        """Test creating a kernel with non-existent Python executable"""
        invalid_path = "/path/to/nonexistent/python"
        
        with pytest.raises(ValueError, match="Python executable not found"):
            create_kernel(invalid_path, "test-kernel")
    
    def test_kernel_creation_auto_id(self):
        """Test creating a kernel with auto-generated ID"""
        python_path = sys.executable
        
        kernel_id = create_kernel(python_path)
        
        assert kernel_id is not None
        assert len(kernel_id) == 8  # UUID short form
        assert kernel_id in kernels
        
        # Clean up
        shutdown_kernel(kernel_id)
    
    def test_duplicate_kernel_id(self):
        """Test that duplicate kernel IDs are rejected"""
        python_path = sys.executable
        
        kernel_id = create_kernel(python_path, "test-kernel")
        
        with pytest.raises(ValueError, match="already exists"):
            create_kernel(python_path, "test-kernel")
        
        # Clean up
        shutdown_kernel(kernel_id)
    
    def test_kernel_shutdown(self):
        """Test shutting down a kernel"""
        python_path = sys.executable
        kernel_id = create_kernel(python_path, "test-kernel")
        
        shutdown_kernel(kernel_id)
        
        assert kernel_id not in kernels
    
    def test_shutdown_nonexistent_kernel(self):
        """Test shutting down a non-existent kernel"""
        with pytest.raises(ValueError, match="not found"):
            shutdown_kernel("nonexistent-kernel")


class TestCodeExecution:
    """Test code execution in kernels"""
    
    def setup_method(self):
        """Set up a test kernel"""
        # Clear any existing kernels
        kernel_ids = list(kernels.keys())
        for kid in kernel_ids:
            try:
                shutdown_kernel(kid)
            except:
                pass
        kernels.clear()
        
        # Create test kernel
        python_path = sys.executable
        self.kernel_id = create_kernel(python_path, "test-kernel")
    
    def teardown_method(self):
        """Clean up test kernel"""
        try:
            shutdown_kernel(self.kernel_id)
        except:
            pass
    
    def test_simple_code_execution(self):
        """Test executing simple Python code"""
        code = "print('Hello, World!')"
        
        result = execute_code_in_kernel(code, self.kernel_id)
        
        assert result['success'] is True
        assert 'Hello, World!' in ''.join(result['output'])
        assert result['error'] is None
    
    def test_variable_persistence(self):
        """Test that variables persist between executions"""
        # Set a variable
        code1 = "test_var = 42"
        result1 = execute_code_in_kernel(code1, self.kernel_id)
        assert result1['success'] is True
        
        # Use the variable in next execution
        code2 = "print(f'Variable value: {test_var}')"
        result2 = execute_code_in_kernel(code2, self.kernel_id)
        assert result2['success'] is True
        assert 'Variable value: 42' in ''.join(result2['output'])
    
    def test_return_value_capture(self):
        """Test capturing return values from expressions"""
        code = "2 + 2"
        
        result = execute_code_in_kernel(code, self.kernel_id)
        
        assert result['success'] is True
        assert result['result'] == '4'
    
    def test_error_handling(self):
        """Test error handling for invalid code"""
        code = "undefined_variable + 1"
        
        result = execute_code_in_kernel(code, self.kernel_id)
        
        assert result['success'] is False
        assert result['error'] is not None
        assert result['error']['name'] == 'NameError'
    
    # TODO: Fix timeout handling in future version
    # def test_timeout_handling(self):
    #     """Test timeout handling for long-running code"""
    #     # Code that would run longer than timeout
    #     code = "import time; time.sleep(10)"
    #     
    #     result = execute_code_in_kernel(code, self.kernel_id, timeout=1)
    #     
    #     assert result['success'] is False
    #     assert 'timeout' in result['error']['message'].lower()
    
    def test_execute_nonexistent_kernel(self):
        """Test executing code in non-existent kernel"""
        code = "print('test')"
        
        with pytest.raises(ValueError, match="not found"):
            execute_code_in_kernel(code, "nonexistent-kernel")


@pytest.fixture
def temp_python_env():
    """Create a temporary Python environment for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Create a fake Python executable (just for path testing)
    fake_python = os.path.join(temp_dir, "python")
    
    # Create executable file
    with open(fake_python, 'w') as f:
        f.write("#!/bin/bash\necho 'fake python'\n")
    os.chmod(fake_python, 0o755)
    
    yield fake_python
    
    # Clean up
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def real_python_env():
    """Create a real temporary Python virtual environment for integration testing"""
    import subprocess
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    venv_path = Path(temp_dir) / "test_venv"
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Get Python executable path (cross-platform)
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_path / "bin" / "python"
        
        # Install ipykernel in the venv (required for Jupyter kernels)
        subprocess.run([str(python_exe), "-m", "pip", "install", "ipykernel"], check=True)
        
        yield str(python_exe)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestEnvironmentHandling:
    """Test Python environment handling"""
    
    def test_valid_python_path_detection(self):
        """Test detection of valid Python executable"""
        python_path = sys.executable
        
        # Should not raise an exception
        kernel_id = create_kernel(python_path, "env-test")
        shutdown_kernel(kernel_id)
    
    def test_invalid_python_path_detection(self):
        """Test detection of invalid Python path"""
        with pytest.raises(ValueError, match="not found"):
            create_kernel("/nonexistent/python", "env-test")
    
    def test_non_executable_python_path(self, temp_python_env):
        """Test detection of non-executable Python path"""
        # Remove execute permission
        os.chmod(temp_python_env, 0o644)
        
        with pytest.raises(ValueError, match="not executable"):
            create_kernel(temp_python_env, "env-test")
    
    def test_kernel_uses_specific_python_env(self, real_python_env):
        """Test that kernel actually uses a specific Python environment"""
        kernel_id = create_kernel(real_python_env, "env-verify-test")
        
        # Execute code to check which Python the kernel is actually using
        check_code = """
import sys
sys.executable
"""
        
        try:
            result = execute_code_in_kernel(check_code, kernel_id)
            assert result['success'] is True
            
            kernel_python = result['result'].strip().strip("'\"")
            assert kernel_python == real_python_env, f"Expected {real_python_env}, got {kernel_python}"
            
        finally:
            shutdown_kernel(kernel_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])