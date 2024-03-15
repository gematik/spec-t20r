import os
import sys
import logging
import coloredlogs
import argparse
import yaml
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse
from typing import Optional

app = FastAPI()

class Bundles:
    """Class to handle the bundle storage and retrieval."""
    def __init__(self, bundle_storage_path, application, version, bundle_type):
        """Initialize the Bundles class."""
        self.bundle_storage_path = bundle_storage_path
        self.application = application
        self.version = version
        self.bundle_type = bundle_type

    def get_bundle_path(self):
        """Return the path to the bundle."""
        return os.path.join(
            self.bundle_storage_path,
            self.application,
            self.version,
            self.bundle_type,
            "bundle.tar.gz",
        )

    def get_bundle_revision(self):
        """Return the revision of the bundle."""
        return os.path.getmtime(self.get_bundle_path())

@app.get("/{application}/{version}/{bundleType}/bundle.tar.gz")
async def get_bundle(
    application: str,
    version: str,
    bundleType: str,
    if_none_match: Optional[str] = Header(None)
):
    """Get the requested bundle."""
    bundle_storage_path = app.state.config["bundle_storage_path"]
    bundle = Bundles(bundle_storage_path, application, version, bundleType)
    bundle_path = bundle.get_bundle_path()

    if bundleType not in ["pip", "pap"]:
        raise HTTPException(status_code=400, detail="Invalid bundle type")

    if not os.path.exists(bundle_path):
        raise HTTPException(status_code=404, detail="The requested bundle does not exist.")

    etag = str(bundle.get_bundle_revision())

    if if_none_match == etag:
        return Response(status_code=304)

    return FileResponse(bundle_path, headers={"ETag": etag})

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
    parser.add_argument("--port", default="8200", help="The TCP port of the server.")
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