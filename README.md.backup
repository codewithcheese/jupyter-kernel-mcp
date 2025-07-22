# Jupyter Kernel MCP

[![PyPI version](https://badge.fury.io/py/jupyter-kernel-mcp.svg)](https://badge.fury.io/py/jupyter-kernel-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides stateful Jupyter kernel development with multi-kernel support for AI agents and assistants.

## Table of contents

1. [Project description](#project-description)
2. [Who this project is for](#who-this-project-is-for)
3. [Project dependencies](#project-dependencies)
4. [Instructions for using Jupyter Kernel MCP](#instructions-for-using-jupyter-kernel-mcp)
5. [Troubleshooting](#troubleshooting)
6. [Contributing guidelines](#contributing-guidelines)
7. [Additional documentation](#additional-documentation)
8. [How to get help](#how-get-help)
9. [Terms of use](#terms-of-use)

## Project description

With _Jupyter Kernel MCP_ you can execute Python code in persistent, isolated environments that maintain state between executionsperfect for AI agents performing complex data analysis workflows.

_Jupyter Kernel MCP_ helps you build stateful AI agent workflows that can load datasets, perform transformations, and analyze results across multiple interactions without losing variables or computed state.

Unlike traditional stateless code execution, _Jupyter Kernel MCP_ preserves variables, imports, and computed results between AI agent messages, enabling sophisticated multi-step data science workflows.

### Key Features

- **= Persistent State**: Variables and imports persist between code executions
- **=€ Multi-Kernel Support**: Create and manage multiple isolated kernel environments  
- **> AI-Agent Ready**: Seamless integration with Claude Code and other MCP clients
- **=Ê Data Science Workflows**: Perfect for iterative data analysis and exploration
- **¡ Fast Communication**: Direct socket-based communication with Jupyter kernels
- **=à Easy Management**: Simple kernel lifecycle management (start, stop, reset, list)

## Who this project is for

This project is intended for AI developers, data scientists, and automation engineers who want to build intelligent agents that can perform stateful data analysis and complex computational workflows.

Perfect for:
- Building AI agents that analyze datasets across multiple interactions
- Creating persistent computational environments for LLMs
- Developing stateful data science workflows with AI assistants
- Prototyping and exploring APIs with maintained context

## Project dependencies

Before using Jupyter Kernel MCP, ensure you have:

* **Python 3.10 or higher** - Required for MCP SDK compatibility
* **Claude Code, Cline, or another MCP client** - To interact with the server
* **Jupyter dependencies** - Automatically installed with the package

## Instructions for using Jupyter Kernel MCP

Get started with Jupyter Kernel MCP by installing the package and adding it to your MCP client.

### Install Jupyter Kernel MCP

1. **Install using pip:**

    ```bash
    pip install jupyter-kernel-mcp
    ```

    Or using uv (recommended):

    ```bash
    uv add jupyter-kernel-mcp
    ```

2. **Verify installation:**

    ```bash
    jupyter-kernel-mcp --help
    ```

### Configure with Claude Code

1. **Add the server to Claude Code:**

    ```bash
    claude mcp add jupyter-kernel jupyter-kernel-mcp
    ```

2. **Verify the server is listed:**

    ```bash
    claude mcp list
    ```

### Configure with other MCP clients

1. **Add to your MCP client configuration** (example for `mcp_config.json`):

    ```json
    {
      "servers": {
        "jupyter-kernel": {
          "command": "jupyter-kernel-mcp"
        }
      }
    }
    ```

### Run Jupyter Kernel MCP

1. **The server starts automatically when called by your MCP client**

    No manual startup required - the server launches when your MCP client connects.

2. **Start your first kernel:**

    In Claude Code or your MCP client:
    ```
    Please start a new Jupyter kernel for data analysis
    ```

3. **Execute stateful code:**

    ```
    Load this dataset and show me the first few rows:
    
    import pandas as pd
    df = pd.read_csv('data.csv')
    df.head()
    ```

4. **Continue the analysis in follow-up messages:**

    ```
    Now group the data by category and calculate the mean values
    ```

    The `df` variable persists from the previous execution!

### Available Tools

| Tool | Description |
|------|-------------|
| `start_kernel` | Create a new Jupyter kernel (with optional custom ID) |
| `execute_python` | Execute Python code in a specific kernel |
| `list_kernels` | Show all active kernels |
| `list_variables` | Display variables in a kernel's namespace |
| `get_kernel_status` | Get detailed kernel information |
| `stop_kernel` | Stop and remove a specific kernel |
| `reset_kernel` | Reset a kernel (clears all variables) |

### Troubleshooting

<table>
  <tr>
   <td><strong>Issue</strong></td>
   <td><strong>Solution</strong></td>
  </tr>
  <tr>
   <td>Server won't start - "No module named 'jupyter_client'"</td>
   <td>Install dependencies: <code>pip install jupyter-client</code></td>
  </tr>
  <tr>
   <td>Kernel creation fails</td>
   <td>Ensure Python 3.10+ is installed and accessible</td>
  </tr>
  <tr>
   <td>MCP client can't find server</td>
   <td>Verify installation: <code>which jupyter-kernel-mcp</code></td>
  </tr>
  <tr>
   <td>Variables not persisting between executions</td>
   <td>Ensure you're using the same kernel_id for related executions</td>
  </tr>
</table>

**Other troubleshooting resources:**
* Check server logs for detailed error messages
* Verify your MCP client supports the required MCP protocol version
* Ensure no firewall is blocking local kernel connections

## Contributing guidelines

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- How to submit bug reports and feature requests
- Development setup and testing procedures  
- Code style guidelines and review process

## Additional documentation

For more information:

* [Model Context Protocol Specification](https://modelcontextprotocol.io/) - Official MCP documentation
* [Jupyter Client Documentation](https://jupyter-client.readthedocs.io/) - Jupyter kernel communication protocol
* [Claude Code MCP Guide](https://docs.anthropic.com/en/docs/claude-code/mcp) - Using MCP servers with Claude

## How to get help

Need assistance? Here's how to get support:

* **GitHub Issues** - [Report bugs or request features](https://github.com/codewithcheese/jupyter-kernel-mcp/issues)
* **Email** - Contact the maintainer at [tom@codewithcheese.com](mailto:tom@codewithcheese.com)
* **MCP Community** - Join discussions in MCP community forums

## Terms of use

Jupyter Kernel MCP is licensed under the [MIT License](LICENSE).

---

*Built with d for the AI agent development community*