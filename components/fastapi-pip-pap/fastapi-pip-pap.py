import os
import sys
import logging
import coloredlogs
import argparse
import yaml
import hashlib
import requests
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse
from typing import Optional
from tempfile import NamedTemporaryFile

app = FastAPI()

class Bundles:
    """Class to handle the bundle storage and retrieval from GitHub."""
    def __init__(self, github_repo, application, label, filename):
        """Initialize the Bundles class."""
        self.github_repo = github_repo
        self.application = application
        self.label = label
        self.filename = filename
        self.bundle_url = self.get_bundle_url()

    def get_bundle_url(self):
        """Return the URL to the bundle."""
        return f"{self.github_repo}/opa_bundles/{self.application}/{self.label}/{self.filename}"

    def download_bundle(self):
        """Download the bundle from GitHub."""
        response = requests.get(self.bundle_url)
        """https://raw.githubusercontent.com/gem-cp/zt-opa-bundles/main/opa_bundles/vsdm/latest/bundle.tar.gz"""
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        temp_file = NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            f.write(response.content)
        
        return temp_file.name

    def get_etag(self, file):
        """Calculates the ETag header value based on the file content hash.
        
        Args:
            file (str): The file to calculate the ETag for.

        Returns:
            str: The ETag header value.
        """
        # Calculate hash of the content
        hasher = hashlib.sha256(file)
        etag = hasher.hexdigest()
        return etag

@app.options("/policies/{application}/{label}")
async def options_bundle(
    application: str,
    label: str
):
    """Handle OPTIONS request for bundle endpoint."""
    return Response(status_code=200, headers={"Allow": "GET, OPTIONS"})

@app.get("/policies/{application}/{label}")
async def get_bundle(
    application: str,
    label: str,
    if_none_match: Optional[str] = Header(None)
):
    """Get the requested bundle."""
    filename = "bundle.tar.gz"
    github_repo = app.state.config["github_repo"]
    bundle = Bundles(github_repo, application, label, filename)

    bundle_file = bundle.download_bundle()

    # Calculate ETag header value
    etag = bundle.get_etag(bundle_file)

    if if_none_match == etag:
        return Response(status_code=304)

    # Add Content-Disposition header
    response = FileResponse(bundle_file, media_type="application/gzip", headers={
        "ETag": etag,
        "Content-Disposition": f"attachment; filename={filename}"
    })
    
    # Clean up the temporary file after sending the response
    response.background = lambda: os.remove(bundle_file)
    
    return response

def load_config(filename):
    """Load the configuration from the given file."""
    try:
        with open(filename, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Configfile {filename} not found.")
        parser.print_help()
        sys.exit(1)

    return config

def setup_logging(log_config):
    """Setup the logging."""
    # Set log level
    log_level = log_config.get("loglevel", "INFO").upper()
    if log_config.get("log_to_console", False):
        coloredlogs.install(level=log_level)
    logger = logging.getLogger("pip-pap-service")
    if log_config.get("log_to_file", False):
        file_handler = logging.FileHandler(f"{log_config['service_name']}.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="mailrobot for automatic email testing.")
    parser.add_argument("--configfile", default="config.yaml", help="The configfile for tsp-cli.")
    parser.add_argument("--servername", default="localhost", help="The IP address or FQDN of the server.")
    parser.add_argument("--port", default="8080", help="The TCP port of the server.")
    args = parser.parse_args()
    # Load the configuration
    config = load_config(args.configfile)
    # Set up logging
    logger = setup_logging(config.get("logging", {}))

    # Set the configuration in the app state
    app.state.config = config

    logger.info("Starting fastapi-pip-pap server ...")

    import uvicorn
    # Start the server
    uvicorn.run(app, host=args.servername, port=int(args.port), log_level=logger.level)
