# Jupyter Kernel MCP

This project implements Model Context Protocol (MCP) tools for Jupyter kernels, enabling AI agents to interact with multi-language Jupyter notebook environments supporting Python, TypeScript, and JavaScript.

## Multi-Language Support

The server provides unified API access to:
- **Python kernels** - Traditional Jupyter Python environments
- **TypeScript kernels** - Via TSLAB with full type checking
- **JavaScript kernels** - Via TSLAB with modern ES6+ support

## Key Implementation Notes

- Single `start_kernel()` tool with `language` parameter ("python", "typescript", "javascript")
- Single `execute_code()` tool that auto-routes to appropriate kernel
- Environment validation per language type
- Backward compatibility maintained for existing Python workflows
- TSLAB integration uses standard Jupyter kernel protocol

# Vendor Documentation

## TSLAB (TypeScript Lab)
- **Location**: [docs/vendor/tslab/](docs/vendor/tslab/)
- **Description**: TypeScript kernel for Jupyter notebooks
- **Key Files**: advanced.md, developing.md, internal.md
- **Repository**: ~/Documents/GitHub/yunabe/tslab/docs/

The TSLAB documentation provides insights into TypeScript-based Jupyter kernel implementation, which may be relevant for understanding kernel architecture and development patterns.
EOF < /dev/null