import os
import sys
import logging
import coloredlogs
import argparse
import yaml
import hashlib
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse
from typing import Optional

app = FastAPI()

class Bundles:
    """Class to handle the bundle storage and retrieval."""
    def __init__(self, bundle_storage_path, policies, application, label, filename):
        """Initialize the Bundles class."""
        self.bundle_storage_path = bundle_storage_path
        self.policies = policies
        self.application = application
        self.label = label
        self.filename = filename
        self.bundle_path = self.get_bundle_path()

    def get_bundle_path(self):
        """Return the path to the bundle."""
        return os.path.join(
            self.bundle_storage_path,
            self.policies,
            self.application,
            self.label,
            self.filename
        )

    def get_etag(self):
      """Calculates the ETag header value based on the file content hash.

      Returns:
          str: The ETag header value.
      """
      # Simulate reading file content
      with open(self.bundle_path, 'rb') as f:
        content = f.read()
      # Calculate hash of the content
      hasher = hashlib.sha256(content)
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

    filename = "bundle.tar.gz"
    """Get the requested bundle."""
    bundle_storage_path = app.state.config["bundle_storage_path"]
    bundle = Bundles(bundle_storage_path, "policies", application, label, filename)
    bundle_path = bundle.get_bundle_path()

    if not os.path.exists(bundle_path):
        raise HTTPException(status_code=404, detail="The requested bundle does not exist.")

    etag = bundle.get_etag()

    if if_none_match == etag:
        return Response(status_code=304)

    # Add Content-Disposition header
    return FileResponse(bundle_path, media_type="application/gzip", headers={
      "ETag": etag,
      #"Content-Disposition": f'attachment; filename="{os.path.basename(bundle_path)}"'
      "Content-Disposition": f"attachment; filename={filename}"
    })

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