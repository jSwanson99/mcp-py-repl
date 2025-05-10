import io
import os
import subprocess
import re
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import List

from fastmcp import FastMCP, Context
import mcp.types as types

from mcp_py_repl.instrumentation import init_otel

enable_otel = os.getenv("OTEL_ENABLED", "true").lower() == "true"
if enable_otel:
    init_otel()

# The Roots functionality in here is crude, awaiting for API support.
# Initialize with settings
mcp = FastMCP(
    "mcp-py-repl",
    log_level="ERROR"
)

# TODO ?
# Shared namespace for all executions
# When a user runs code via the execute_python tool, this shared namespace allows for a persistent interactive session rather than each execution starting from scratch
global_namespace = {
    "__builtins__": __builtins__,
}


# {{{ """Execute Python code and return the output. Variables persist between executions."""
@mcp.tool()
async def execute_python(ctx: Context, code: str, reset: bool = False) -> List[types.TextContent]:
    """Execute Python code and return the output. Variables persist between executions."""
    global global_namespace

    await set_working_dir_from_roots(ctx)  # Update directory if needed

    if reset:
        global_namespace.clear()
        global_namespace["__builtins__"] = __builtins__
        return [types.TextContent(type="text", text="Python session reset. All variables cleared.")]

    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(code, global_namespace)

        output = stdout.getvalue()
        errors = stderr.getvalue()

        result = ""
        if output:
            result += f"Output:\n{output}"
        if errors:
            result += f"\nErrors:\n{errors}"
        if not output and not errors:
            try:
                last_line = code.strip().split('\n')[-1]
                last_value = eval(last_line, global_namespace)
                result = f"Result: {repr(last_value)}"
            except (SyntaxError, ValueError, NameError):
                result = "Code executed successfully (no output)"

        return [types.TextContent(type="text", text=result)]

    except Exception:
        error_msg = f"Error executing code:\n{traceback.format_exc()}"
        return [types.TextContent(type="text", text=error_msg)]
# }}}


# {{{ """Install a Python package using uv"""
@mcp.tool()
async def install_package(ctx: Context, package: str) -> List[types.TextContent]:
    """Install a Python package using uv"""

    await set_working_dir_from_roots(ctx)  # Update directory if needed

    if not re.match("^[A-Za-z0-9][A-Za-z0-9._-]*$", package):
        return [types.TextContent(type="text", text=f"Invalid package name: {package}")]

    try:
        print(f"Installing package: {package}", file=sys.stderr)
        process = subprocess.run(
            ["uv", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )

        if process.returncode != 0:
            return [types.TextContent(type="text", text=f"Failed to install package: {process.stderr}")]

        try:
            exec(f"import {package.split('[')[0]}", global_namespace)
            return [types.TextContent(type="text", text=f"Successfully installed and imported {package}")]
        except ImportError as e:
            return [types.TextContent(type="text", text=f"Package installed but import failed: {str(e)}")]

    except subprocess.CalledProcessError as e:
        return [types.TextContent(type="text", text=f"Failed to install package:\n{e.stderr}")]
# }}}


# {{{ """List all variables in the current session"""
@mcp.tool()
async def list_variables(ctx: Context) -> List[types.TextContent]:
    """List all variables in the current session"""
    vars_dict = {
        k: repr(v) for k, v in global_namespace.items()
        if not k.startswith('_') and k != '__builtins__'
    }

    if not vars_dict:
        return [types.TextContent(type="text", text="No variables in current session.")]

    var_list = "\n".join(f"{k} = {v}" for k, v in vars_dict.items())
    return [types.TextContent(type="text", text=f"Current session variables:\n\n{var_list}")]
# }}}


# {{{ set_working_dir_from_roots(
async def set_working_dir_from_roots(ctx: Context) -> None:
    """Get roots and set working directory to first root if available."""
    try:
        roots_result: types.ListRootsResult = await ctx.session.list_roots()

        # Check the roots list exists and has items
        if roots_result and hasattr(roots_result, 'roots') and roots_result.roots:
            root = roots_result.roots[0]
            uri_str = str(root.uri)
            if uri_str.startswith("file://"):
                path = uri_str.replace("file://", "")
                path = os.path.normpath(path)
                current_dir = os.path.normpath(os.getcwd())
                if path != current_dir:
                    try:
                        os.chdir(path)
                    except OSError as e:
                        print(f"Failed to change directory to {path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error handling roots: {str(e)}", file=sys.stderr)
# }}}

def main():
    """Main entry point for the server."""
    import asyncio
    asyncio.run(mcp.run_sse_async(host="0.0.0.0", port=8000, log_level="debug"))


if __name__ == "__main__":
    main()
