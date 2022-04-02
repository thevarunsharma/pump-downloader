import os
import re
from typing import Dict, List
from urllib.parse import urlparse


def parse_headers(header_input: List[str]) -> Dict[str, str]:
    """Parses header inputs to command to be supplied to the HTTP request

    Parameter
    ---------
    header_input: list[str]
        list containing header values

    Returns
    -------
    Dict[str, str]
        Headers parsed as a dictionary
    """
    headers = {}
    pattern = re.compile(r'^(.*?):(.*)$')
    for header_str in header_input:
        match = pattern.match(header_str)
        if match is None:
            raise ValueError(f"Invalid header value: {header_str}")
        key, value = match[1].strip(), match[2].lstrip()
        if key == "Range":
            raise ValueError("Header value not allowed: Range")
        headers[key] = value
    return headers

def get_base_filename(url: str) -> str:
    """Checks validity of resource URL and returns the base filename
    
    Parameters
    ----------
    url : str
        resource URL supplied by the user
        
    Returns
    -------
    bool
        Base filename for the file referenced by ``url``,
        raises ``ValueError`` if ``url`` is invalid
    """
    try:
        result = urlparse(url)
        isvalid = all([result.scheme, result.netloc])
        if isvalid:
            # if it's a valid URL then return the file path to save it with
            return result.path
    except:
        pass
    # raise error if it's an invalid URL or there was an error while parsing
    raise ValueError("Invalid Resource URL")

def get_available_path(path: str) -> str:
    """Get an available savepath"""
    newpath = path = os.path.basename(path)
    i = 1
    while os.path.exists(newpath):
        newpath = path + f"_{i}"
        i += 1
    return newpath
    

def format_bytes(size: int) -> (float, str):
    """Format ``size`` to nearest byte unit"""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]+'B'
