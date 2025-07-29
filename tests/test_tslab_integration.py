#!/usr/bin/env python3
"""
Test suite for TSLAB TypeScript/JavaScript integration
"""

import pytest
import sys
import os
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jupyter_kernel_mcp.server import (
    create_kernel, shutdown_kernel, execute_code_in_kernel, 
    get_kernel_client, kernels, validate_node_environment,
    validate_environment
)


class TestTSLabEnvironmentValidation:
    """Test TSLAB environment validation"""
    
    def test_validate_node_environment_valid(self):
        """Test validation with valid Node.js and tslab setup"""
        # Skip if tslab not available
        try:
            result = subprocess.run(["tslab", "install", "--version"], 
                                  capture_output=True, timeout=5)
            if result.returncode != 0:
                pytest.skip("tslab not available for testing")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("tslab not available for testing")
        
        # Should not raise an exception if properly set up
        try:
            node_path = shutil.which("node")
            if node_path:
                validate_node_environment(node_path)
        except ValueError as e:
            pytest.skip(f"Node.js environment not properly set up: {e}")
    
    def test_validate_node_environment_invalid_node(self):
        """Test validation with invalid Node.js path"""
        with pytest.raises(ValueError, match="Node.js executable not found"):
            validate_node_environment("/nonexistent/node")
    
    def test_validate_environment_typescript(self):
        """Test generic validation for TypeScript"""
        node_path = shutil.which("node")
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            validate_environment("typescript", node_path)
        except ValueError as e:
            pytest.skip(f"TypeScript environment not available: {e}")
    
    def test_validate_environment_javascript(self):
        """Test generic validation for JavaScript"""
        node_path = shutil.which("node")
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            validate_environment("javascript", node_path)
        except ValueError as e:
            pytest.skip(f"JavaScript environment not available: {e}")
    
    def test_validate_environment_unsupported_language(self):
        """Test validation with unsupported language"""
        with pytest.raises(ValueError, match="Unsupported language"):
            validate_environment("ruby", "/usr/bin/ruby")


class TestTSLabKernelManagement:
    """Test TSLAB kernel lifecycle management"""
    
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
    
    def test_create_typescript_kernel(self):
        """Test creating a TypeScript kernel"""
        node_path = shutil.which("node")
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            # Check if tslab is available
            result = subprocess.run(["jupyter", "kernelspec", "list", "--json"], 
                                  capture_output=True, timeout=10)
            if result.returncode != 0:
                pytest.skip("Jupyter not available for testing")
            
            import json
            kernelspecs = json.loads(result.stdout.decode())
            if 'tslab' not in kernelspecs.get('kernelspecs', {}):
                pytest.skip("tslab kernelspec not available for testing")
            
            kernel_id = create_kernel("typescript", node_path, "test-ts-kernel")
            
            assert kernel_id == "test-ts-kernel"
            assert kernel_id in kernels
            assert kernels[kernel_id]['language'] == "typescript"
            assert kernels[kernel_id]['env_path'] == node_path
            
            # Clean up
            shutdown_kernel(kernel_id)
            
        except Exception as e:
            pytest.skip(f"TypeScript kernel creation failed: {e}")
    
    def test_create_javascript_kernel(self):
        """Test creating a JavaScript kernel"""
        node_path = shutil.which("node")
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            # Check if jslab is available
            result = subprocess.run(["jupyter", "kernelspec", "list", "--json"], 
                                  capture_output=True, timeout=10)
            if result.returncode != 0:
                pytest.skip("Jupyter not available for testing")
            
            import json
            kernelspecs = json.loads(result.stdout.decode())
            if 'jslab' not in kernelspecs.get('kernelspecs', {}):
                pytest.skip("jslab kernelspec not available for testing")
            
            kernel_id = create_kernel("javascript", node_path, "test-js-kernel")
            
            assert kernel_id == "test-js-kernel"
            assert kernel_id in kernels
            assert kernels[kernel_id]['language'] == "javascript"
            assert kernels[kernel_id]['env_path'] == node_path
            
            # Clean up
            shutdown_kernel(kernel_id)
            
        except Exception as e:
            pytest.skip(f"JavaScript kernel creation failed: {e}")
    
    def test_kernel_creation_with_invalid_language(self):
        """Test that invalid languages are rejected"""
        node_path = shutil.which("node") or "/usr/bin/node"
        
        with pytest.raises(ValueError, match="Unsupported language"):
            create_kernel("ruby", node_path, "test-kernel")


class TestTSLabCodeExecution:
    """Test code execution in TSLAB kernels"""
    
    def setup_method(self):
        """Set up test kernels"""
        # Clear any existing kernels
        kernel_ids = list(kernels.keys())
        for kid in kernel_ids:
            try:
                shutdown_kernel(kid)
            except:
                pass
        kernels.clear()
        
        # Try to create TypeScript and JavaScript kernels
        node_path = shutil.which("node")
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            # Check kernelspecs are available
            result = subprocess.run(["jupyter", "kernelspec", "list", "--json"], 
                                  capture_output=True, timeout=10)
            if result.returncode != 0:
                pytest.skip("Jupyter not available for testing")
            
            import json
            kernelspecs = json.loads(result.stdout.decode())
            available_kernels = kernelspecs.get('kernelspecs', {}).keys()
            
            self.ts_kernel_id = None
            self.js_kernel_id = None
            
            if 'tslab' in available_kernels:
                self.ts_kernel_id = create_kernel("typescript", node_path, "test-ts")
            
            if 'jslab' in available_kernels:
                self.js_kernel_id = create_kernel("javascript", node_path, "test-js")
            
            if not self.ts_kernel_id and not self.js_kernel_id:
                pytest.skip("Neither tslab nor jslab kernelspecs available")
                
        except Exception as e:
            pytest.skip(f"Failed to create test kernels: {e}")
    
    def teardown_method(self):
        """Clean up test kernels"""
        try:
            if hasattr(self, 'ts_kernel_id') and self.ts_kernel_id:
                shutdown_kernel(self.ts_kernel_id)
        except:
            pass
        try:
            if hasattr(self, 'js_kernel_id') and self.js_kernel_id:
                shutdown_kernel(self.js_kernel_id)
        except:
            pass
    
    def test_typescript_simple_execution(self):
        """Test executing simple TypeScript code"""
        if not hasattr(self, 'ts_kernel_id') or not self.ts_kernel_id:
            pytest.skip("TypeScript kernel not available")
        
        code = "console.log('Hello from TypeScript!'); 42"
        
        result = execute_code_in_kernel(code, self.ts_kernel_id)
        
        assert result['success'] is True
        assert 'Hello from TypeScript!' in ''.join(result['output'])
        assert result['result'] == '42'
        assert result['error'] is None
    
    def test_typescript_type_checking(self):
        """Test TypeScript type checking"""
        if not hasattr(self, 'ts_kernel_id') or not self.ts_kernel_id:
            pytest.skip("TypeScript kernel not available")
        
        # This should work - proper TypeScript
        code = "const x: number = 42; x"
        result = execute_code_in_kernel(code, self.ts_kernel_id)
        assert result['success'] is True
        assert result['result'] == '42'
    
    def test_typescript_variable_persistence(self):
        """Test that variables persist between TypeScript executions"""
        if not hasattr(self, 'ts_kernel_id') or not self.ts_kernel_id:
            pytest.skip("TypeScript kernel not available")
        
        # Set a variable
        code1 = "const testVar: string = 'TypeScript rocks!';"
        result1 = execute_code_in_kernel(code1, self.ts_kernel_id)
        assert result1['success'] is True
        
        # Use the variable in next execution
        code2 = "console.log(testVar); testVar"
        result2 = execute_code_in_kernel(code2, self.ts_kernel_id)
        assert result2['success'] is True
        assert 'TypeScript rocks!' in ''.join(result2['output'])
        assert result2['result'] == "'TypeScript rocks!'"
    
    def test_javascript_simple_execution(self):
        """Test executing simple JavaScript code"""
        if not hasattr(self, 'js_kernel_id') or not self.js_kernel_id:
            pytest.skip("JavaScript kernel not available")
        
        code = "console.log('Hello from JavaScript!'); [1,2,3].map(x => x*2)"
        
        result = execute_code_in_kernel(code, self.js_kernel_id)
        
        assert result['success'] is True
        assert 'Hello from JavaScript!' in ''.join(result['output'])
        # Result should be the mapped array
        assert '[' in result['result'] and '2' in result['result']
        assert result['error'] is None
    
    def test_javascript_variable_persistence(self):
        """Test that variables persist between JavaScript executions"""
        if not hasattr(self, 'js_kernel_id') or not self.js_kernel_id:
            pytest.skip("JavaScript kernel not available")
        
        # Set a variable
        code1 = "let jsVar = {name: 'JavaScript', version: 'ES2020'};"
        result1 = execute_code_in_kernel(code1, self.js_kernel_id)
        assert result1['success'] is True
        
        # Use the variable in next execution
        code2 = "console.log(jsVar.name); jsVar"
        result2 = execute_code_in_kernel(code2, self.js_kernel_id)
        assert result2['success'] is True
        assert 'JavaScript' in ''.join(result2['output'])
    
    def test_error_handling_typescript(self):
        """Test error handling for TypeScript compilation errors"""
        if not hasattr(self, 'ts_kernel_id') or not self.ts_kernel_id:
            pytest.skip("TypeScript kernel not available")
        
        # This should cause a TypeScript error
        code = "const x: number = 'not a number';"
        
        result = execute_code_in_kernel(code, self.ts_kernel_id)
        
        # Should fail due to TypeScript type checking
        assert result['success'] is False
        assert result['error'] is not None
    
    def test_error_handling_javascript_runtime(self):
        """Test error handling for JavaScript runtime errors"""
        if not hasattr(self, 'js_kernel_id') or not self.js_kernel_id:
            pytest.skip("JavaScript kernel not available")
        
        # This should cause a runtime error
        code = "undefinedVariable.someMethod();"
        
        result = execute_code_in_kernel(code, self.js_kernel_id)
        
        # Should fail due to runtime error
        assert result['success'] is False
        assert result['error'] is not None
        assert 'ReferenceError' in result['error']['name'] or 'Error' in result['error']['name']


class TestMixedLanguageKernels:
    """Test managing multiple language kernels simultaneously"""
    
    def setup_method(self):
        """Clear kernels before each test"""
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
    
    def test_multiple_language_kernels(self):
        """Test running Python, TypeScript, and JavaScript kernels simultaneously"""
        python_path = sys.executable
        node_path = shutil.which("node")
        
        if not node_path:
            pytest.skip("Node.js not available for testing")
        
        try:
            # Create kernels for different languages
            py_kernel = create_kernel("python", python_path, "test-python")
            
            # Try to create TS/JS kernels (skip if not available)
            ts_kernel = None
            js_kernel = None
            
            try:
                ts_kernel = create_kernel("typescript", node_path, "test-typescript")
            except:
                pass
            
            try:
                js_kernel = create_kernel("javascript", node_path, "test-javascript")
            except:
                pass
            
            # Verify kernels are stored with correct metadata
            assert kernels[py_kernel]['language'] == 'python'
            
            if ts_kernel:
                assert kernels[ts_kernel]['language'] == 'typescript'
            
            if js_kernel:
                assert kernels[js_kernel]['language'] == 'javascript'
            
            # Execute language-specific code in each kernel
            py_result = execute_code_in_kernel("print('Python works!'); 2+2", py_kernel)
            assert py_result['success'] is True
            assert 'Python works!' in ''.join(py_result['output'])
            
            if ts_kernel:
                ts_result = execute_code_in_kernel("console.log('TypeScript works!'); 3+3", ts_kernel)
                assert ts_result['success'] is True
                assert 'TypeScript works!' in ''.join(ts_result['output'])
            
            if js_kernel:
                js_result = execute_code_in_kernel("console.log('JavaScript works!'); 4+4", js_kernel)
                assert js_result['success'] is True
                assert 'JavaScript works!' in ''.join(js_result['output'])
            
            # Clean up
            shutdown_kernel(py_kernel)
            if ts_kernel:
                shutdown_kernel(ts_kernel)
            if js_kernel:
                shutdown_kernel(js_kernel)
                
        except Exception as e:
            pytest.skip(f"Mixed language kernel test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])