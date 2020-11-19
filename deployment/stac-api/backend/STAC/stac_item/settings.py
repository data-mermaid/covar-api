import os
from urllib.parse import urljoin

def check_value(param, param_name):
    if param is None or param == "":
        raise ValueError(param_name + " not found")
    return param

STAC_URL = check_value(os.environ.get("STAC_URL"), "STAC_URL")

STAC_SEARCH_URL = urljoin(STAC_URL, "stac/search/")

TITILER_ENDPOINT = check_value(os.environ.get("TITILER_ENDPOINT"), "TITILER_ENDPOINT")