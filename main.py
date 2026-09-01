from fastmcp import FastMCP
import json
import random

mcp = FastMCP("Simple testing of FastMCP", "This is a simple test of the FastMCP library.")

@mcp.tool
def random_number_generator():
    """Generates a random number between 1 and 100.

    args:
        None

    returns:
        int: A random integer between 1 and 100. 
    """
    return random.randint(1, 100)

@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers and returns the result.
    
    args:
        a (int): The first number to add.
        b (int): The second number to add.
    returns:
        int: The sum of the two numbers.
    """
    return a + b

@mcp.tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiplies two numbers and returns the result.

    args:
        a (int): The first number to multiply.
        b (int): The second number to multiply.
    returns:
        int: The product of the two numbers.
    """
    return a * b

@mcp.resource("info://server")
def server_info():
    """Returns information about the server."""
    info = {
        "server_name": "FastMCP Test Server",
        "version": "1.0.0",
        "description": "This server is used for testing the FastMCP library.",
        "tools": ["random_number_generator", "add_numbers", "multiply_numbers"],
        "authors": ["Vivek Singh"]
    }

    return json.dumps(info, indent=4)

if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=8000)