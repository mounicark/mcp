
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
        logging.debug("File is not in working directory")
        return "File is not in the working dir"
    
    if not os.path.isfile(abs_file):
        if not os.path.exists(abs_file):
            logging.debug("Not in working directory")
        else:
            logging.debug("Not a file")

        return f"{file} is not a file or file doesn't exist"
    
    try:
        with open(abs_file, "r") as f:
            content = f.read()
            return content
        
    except Exception as e:
        logging.error(f'Error reading the file {e}')
        return f"Error reading file {e}"

def main():
    mcp.run(transport="stdio") 

if __name__ == "__main__":
    main()


    

    
