# MCP Python REPL

An MCP server providing a persistent Python REPL session.

## Installation

```bash
pip install mcp-py-repl
```

## Usage

```bash
mcp-py-repl
```

## Using with Docker

You can run the REPL server using Docker:

```bash
docker pull ghcr.io/evalstate/mcp-py-repl
docker run -it ghcr.io/evalstate/mcp-py-repl
```

The container includes:
- Python 3.12
- UV package manager for fast dependency installation
- Pre-configured environment for MCP

## Features

- Persistent Python session
- Package installation via UV
- Variable inspection
- Directory awareness via MCP roots

## Running the Server

This server is intended to be used via Docker.

```
  args:
    [
      "run",
      "-i",
      "--rm",
      "--pull=always",
      "-v",
      "./test_data:/mnt/data/",
      "ghcr.io/evalstate/mcp-py-repl:latest",
    ]
```

The server provides three tools:

1. `execute_python`: Execute Python code with persistent variables

   - `code`: The Python code to execute
   - `reset`: Optional boolean to reset the session

2. `list_variables`: Show all variables in the current session

3. `install_package`: Install a package from pypi

## Examples

Set a variable:

```python
a = 42
```

Use the variable:

```python
print(f"The value is {a}")
```

List all variables:

```python
# Use the list_variables tool
```

Reset the session:

```python
# Use execute_python with reset=true
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Here are some ways you can contribute:

- Report bugs
- Suggest new features
- Improve documentation
- Add test cases
- Submit code improvements

Before submitting a PR, please ensure:

1. Your code follows the existing style
2. You've updated documentation as needed
3. Maybe write some tests?

For major changes, please open an issue first to discuss what you would like to change.
