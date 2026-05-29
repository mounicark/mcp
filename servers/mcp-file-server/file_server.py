
from typing import Any
from mcp.server.fastmcp import FastMCP
import os
import logging

logging.basicConfig(level=logging.DEBUG, filename="server_logs.log", filemode="w", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
mcp = FastMCP("file-server")

working_dir = '/home/mounica/test/lib'

@mcp.tool()
async def get_file_contents(file: str) -> str:
    """Check if the given file exists and return its content"""
    abs_file = os.path.abspath(os.path.join(working_dir, file))
    logging.debug("Requested file=%s abs_file=%s exists=%s isfile=%s",
                  file, abs_file, os.path.exists(abs_file), os.path.isfile(abs_file))

    if os.path.commonpath([working_dir, abs_file]) != working_dir:
        logging.warning("Rejected path outside working dir: %s", abs_file)
        return "File not found in the working dir"
    
    if not os.path.isfile(abs_file):
        if not os.path.exists(abs_file):
            logging.info("File does not exist: %s", abs_file)
        else:
            logging.warning("Path exists but is not a file: %s", abs_file)

        return f"{file} file doesn't exist in the working directory"
    
    try:
        with open(abs_file, "r") as f:
            content = f.read()
            return content
        
    except Exception as e:
        logging.error(f'Error reading the file {e}')
        return f"Error reading file"
    
@mcp.tool()
async def write_to_file(file: str, content: str) -> str:
    abs_file = os.path.abspath(os.path.join(working_dir, file))

    if os.path.commonpath([abs_file, working_dir]) != working_dir:
        logging.warning("File is not in working directory")
        return "Error: File is outside working directory"

    parent_dir = os.path.dirname(abs_file)

    try:
        os.makedirs(parent_dir, exist_ok=True)
    except Exception:
        logging.exception("Couldn't create directories")
        return f"Could not create directories: {abs_file}"

    try:
        with open(abs_file, "w") as f:
            written = f.write(content)
            return f"Wrote {written} contents to {file}"
        
    except Exception as e:
        logging.exception("Failed to write to file: %s", abs_file)
        return f"Error writing to the file {file}"

def main():
    mcp.run(transport="stdio") 

if __name__ == "__main__":
    main()


    

    
