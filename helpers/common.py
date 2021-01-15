# Common functions related to simple python-related things.
from typing import Union
import os
# orjson didnt work
import json

class JsonFile:
    """Assists within working with simple JSON files."""

    def __init__(self, file_name: str):
        """Loads a Json file `file_name` from disk.
        
        Args:
            file_name (str): The path including the filename
                of the JSON file you would like to load.
        """

        self.file = None
        self.file_name = file_name
        if os.path.exists(file_name):
            with open(file_name) as f:
                self.file = json.load(f)

    def get_file(self) -> dict:
        """Returns the loaded JSON file as a dict.
        
        Returns:
            Contents of the file.
        """
        return self.file

    def write_file(self, new_content: Union[dict, list]) -> None:
        """Writes `new_content` to the target file.
        
        Args:
            new_content (dict, list): The new content that should
                be placed within the file.
        """

        with open(self.file_name, "w") as f:
            json.dump(new_content, f, indent=4)
        self.file = new_content

def dict_keys(d: dict) -> tuple:
    """Returns a `tuple` of all the keys present within
    the dictionary `d`.
    
    Args:
        d (dict): A dictionary to fetch all the keys of.
    """

    # I decided to use tuple as its immutable.
    return tuple(d)