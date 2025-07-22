#!/usr/bin/env python3
"""
MCP Server for stateful Jupyter kernel development
Provides tools for executing Python code with persistent state
"""

import asyncio
from typing import Any, Dict, List
from datetime import datetime
import json

from mcp.server.fastmcp import FastMCP
from jupyter_client import KernelManager
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Dictionary to store multiple kernels
kernels = {}  # kernel_id -> {'manager': KernelManager, 'client': KernelClient, 'created_at': datetime}

import uuid

def create_kernel(kernel_id=None):
    """Create a new Jupyter kernel"""
    if kernel_id is None:
        kernel_id = str(uuid.uuid4())[:8]  # Short ID
    
    if kernel_id in kernels:
        raise ValueError(f"Kernel {kernel_id} already exists")
    
    print(f"Starting Jupyter kernel {kernel_id}...")
    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.wait_for_ready()
    
    kernels[kernel_id] = {
        'manager': km,
        'client': kc, 
        'created_at': datetime.now()
    }
    
    print(f"Jupyter kernel {kernel_id} ready!")
    return kernel_id

def get_kernel_client(kernel_id):
    """Get kernel client by ID"""
    if kernel_id not in kernels:
        raise ValueError(f"Kernel {kernel_id} not found")
    return kernels[kernel_id]['client']

def shutdown_kernel(kernel_id):
    """Stop and remove a kernel"""
    if kernel_id not in kernels:
        raise ValueError(f"Kernel {kernel_id} not found")
    
    kernel_info = kernels[kernel_id]
    kernel_info['client'].stop_channels()
    kernel_info['manager'].shutdown_kernel()
    del kernels[kernel_id]
    
    print(f"Kernel {kernel_id} stopped and removed")

def execute_code_in_kernel(code: str, kernel_id: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute code in Jupyter kernel and return structured result"""
    kc = get_kernel_client(kernel_id)
    
    result = {
        'success': True,
        'output': [],
        'result': None,
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        msg_id = kc.execute(code)
        
        while True:
            try:
                msg = kc.get_iopub_msg(timeout=timeout)
                
                if msg['msg_type'] == 'stream':
                    result['output'].append(msg['content']['text'])
                elif msg['msg_type'] == 'execute_result':
                    result['result'] = msg['content']['data']['text/plain']
                elif msg['msg_type'] == 'error':
                    result['success'] = False
                    result['error'] = {
                        'name': msg['content']['ename'],
                        'message': msg['content']['evalue'],
                        'traceback': msg['content']['traceback']
                    }
                elif msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                    break
            except Exception as e:
                if 'timeout' in str(e).lower():
                    result['success'] = False
                    result['error'] = {'name': 'Timeout', 'message': f'Timeout after {timeout}s'}
                break
                
    except Exception as e:
        result['success'] = False
        result['error'] = {'name': 'ExecutionError', 'message': str(e)}
    
    return result

# Create MCP server
mcp = FastMCP("Jupyter Kernel Server")

@mcp.tool()
def start_kernel(kernel_id: str = None) -> dict:
    """
    Start a new Jupyter kernel.
    
    Args:
        kernel_id: Optional custom kernel ID. If not provided, generates a random ID.
    
    Returns:
        Dictionary with kernel_id and creation info
    """
    try:
        actual_id = create_kernel(kernel_id)
        return {
            'success': True,
            'kernel_id': actual_id,
            'message': f'Kernel {actual_id} started successfully',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@mcp.tool()
def stop_kernel(kernel_id: str) -> dict:
    """
    Stop and remove a Jupyter kernel.
    
    Args:
        kernel_id: ID of the kernel to stop
    
    Returns:
        Dictionary indicating success/failure
    """
    try:
        shutdown_kernel(kernel_id)
        return {
            'success': True,
            'message': f'Kernel {kernel_id} stopped successfully',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@mcp.tool()
def list_kernels() -> dict:
    """
    List all active kernels.
    
    Returns:
        Dictionary with kernel information
    """
    kernel_info = {}
    for kid, kdata in kernels.items():
        kernel_info[kid] = {
            'created_at': kdata['created_at'].isoformat(),
            'status': 'running'
        }
    
    return {
        'success': True,
        'kernels': kernel_info,
        'count': len(kernels),
        'timestamp': datetime.now().isoformat()
    }

@mcp.tool()
def execute_python(code: str, kernel_id: str, timeout: int = 30) -> dict:
    """
    Execute Python code in a persistent Jupyter kernel.
    Variables and state persist between executions.
    
    Args:
        code: Python code to execute
        kernel_id: ID of the kernel to execute code in
        timeout: Execution timeout in seconds (default 30)
    
    Returns:
        Dictionary with execution result:
        - success: boolean indicating if execution succeeded
        - output: list of stdout/stderr lines
        - result: return value of the last expression (if any)
        - error: error information if execution failed
        - timestamp: when the execution occurred
    """
    return execute_code_in_kernel(code, kernel_id, timeout)

@mcp.tool()
def list_variables(kernel_id: str) -> dict:
    """
    List all variables currently defined in the kernel namespace.
    
    Args:
        kernel_id: ID of the kernel to inspect
    
    Returns:
        Dictionary with variable names, types, and string representations
    """
    code = """
import sys
# Create a snapshot of globals to avoid "dictionary changed size during iteration"
globals_snapshot = dict(globals())
namespace_vars = {}
for name, value in globals_snapshot.items():
    if not name.startswith('_') and not callable(value) and name not in sys.modules:
        try:
            namespace_vars[name] = {
                'type': type(value).__name__,
                'repr': str(value)[:100] + ('...' if len(str(value)) > 100 else ''),
                'size': len(str(value))
            }
        except:
            # Skip variables that can't be stringified
            namespace_vars[name] = {
                'type': type(value).__name__,
                'repr': '<unable to display>',
                'size': 0
            }
namespace_vars
"""
    return execute_code_in_kernel(code, kernel_id)

@mcp.tool()
def reset_kernel(kernel_id: str) -> dict:
    """
    Reset a Jupyter kernel by stopping and restarting it with the same ID.
    This clears all variables and state.
    
    Args:
        kernel_id: ID of the kernel to reset
    
    Returns:
        Dictionary indicating the reset was successful
    """
    try:
        # Stop the existing kernel
        shutdown_kernel(kernel_id)
        
        # Start a new kernel with the same ID
        create_kernel(kernel_id)
        
        return {
            'success': True,
            'message': f'Kernel {kernel_id} reset successfully',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@mcp.tool()
def get_kernel_status(kernel_id: str) -> dict:
    """
    Get status information about a specific Jupyter kernel.
    
    Args:
        kernel_id: ID of the kernel to check
    
    Returns:
        Dictionary with kernel status information
    """
    kc = get_kernel_client(kernel_id)
    
    # Get basic info
    info_code = """
import sys, psutil, os
from datetime import datetime

{
    'python_version': sys.version,
    'pid': os.getpid(),
    'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
    'uptime': 'kernel_running',
    'current_time': datetime.now().isoformat()
}
"""
    
    try:
        result = execute_code_in_kernel(info_code, kernel_id)
        if result['success'] and result['result']:
            return json.loads(result['result'].replace("'", '"'))
        else:
            return {'status': 'running', 'details': 'basic info unavailable'}
    except:
        return {'status': 'running', 'details': 'status check failed'}

@mcp.resource("kernel://variables/{kernel_id}")
def get_variables_resource(kernel_id: str) -> str:
    """
    Resource providing current kernel variables as text.
    """
    try:
        result = list_variables(kernel_id)
        if result['success'] and result['result']:
            vars_dict = eval(result['result'])
            output = f"Kernel {kernel_id} Variables:\n\n"
            for name, info in vars_dict.items():
                output += f"{name} ({info['type']}): {info['repr']}\n"
            return output
        else:
            return f"Error reading variables from kernel {kernel_id}"
    except Exception as e:
        return f"Kernel {kernel_id} not found or error: {str(e)}"

# Cleanup function
def cleanup():
    """Cleanup all kernels on exit"""
    for kernel_id in list(kernels.keys()):
        try:
            shutdown_kernel(kernel_id)
        except:
            pass

def main():
    """Main entry point for the MCP server"""
    import atexit
    print("Starting MCP Jupyter Kernel Server...")
    print("No kernels started by default - use start_kernel tool to create kernels")
    
    atexit.register(cleanup)
    print("Starting MCP protocol server...")
    mcp.run()

if __name__ == "__main__":
    main()