from fastapi import FastAPI, Response, Depends, HTTPException, Header
from typing import Optional
import os
import yaml
import argparse
from loguru import logger

def load_config(config_path: str = "config.yaml"):
    """
    Loads configuration settings from a YAML file.
    """
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded config from YAML: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise Exception("Config file not found")

# Dependency for configuration
def get_config():
    return load_config()

app = FastAPI()
config = Depends(get_config)

# Set up logging
def setup_logging(log_config):
    """Setup the logging."""
    # Set log level
    logger.remove()  # Remove existing loggers
    log_level= log_config["log_level"]
    if log_config.get("log_to_console", False):
        logger.add(
            "console",
            level=log_level,
            format="{level} {message}",
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
    if log_config.get("log_to_file", False):
        log_file_path = f"{log_config.get('service_name')}.log"
        logger.add(log_file_path, level=log_level, enqueue=True, rotation="500 MB")

    return logger

@app.get("/{application}/{version}/{bundleType}/bundle.tar.gz")
async def get_bundle(
    application: str,
    version: str,
    bundleType: str,
    if_none_match: Optional[str] = Header(None),
    config: dict = Depends(get_config)
):
    """
    Retrieve a signed {bundleType} OPA bundle for the given application and version.

    This function checks the If-None-Match header to avoid unnecessary downloads.
    """

    # Validate bundle type
    if bundleType not in ("pip", "pap"):
        logger.warning(f"Invalid bundle type: {bundleType}")
        raise HTTPException(status_code=400, detail="Invalid bundle type")

    # Construct bundle file path based on config
    bundle_path = os.path.join(config["bundle_storage_path"],
                               application, version, bundleType, "bundle.tar.gz")

    # Check if bundle exists
    if not os.path.exists(bundle_path):
        logger.warning(f"Bundle not found: {bundle_path}")
        raise HTTPException(status_code=404, detail="The requested bundle does not exist.")

    # Set ETag header (example: use modification time)
    etag = os.path.getmtime(bundle_path)

    # Check If-None-Match header for unchanged bundle
    if if_none_match:
        if if_none_match == str(etag):
            logger.debug(f"Bundle not modified (etag: {etag})")
            return Response(status_code=304)  # Empty body for 304

    # Read bundle content
    with open(bundle_path, "rb") as f:
        bundle_content = f.read()

    logger.debug(f"Returning bundle: {bundle_path} (etag: {etag})")
    response = Response(content=bundle_content, media_type="application/gzip")
    response.headers["ETag"] = str(etag)
    return response

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="mailrobot for automatic email testing.")
    parser.add_argument("--configfile", default="config.yaml", help="The configfile for tsp-cli.")
    parser.add_argument("--servername", default="localhost", help="The IP address or FQDN of the server.")
    parser.add_argument("--port", default="8600", help="The TCP port of the server.")
    args = parser.parse_args()
    # Load the configuration
    config = load_config(args.configfile)
    
    # Set up logging
    logger = setup_logging(config.get("logging", {}))

    logger.info("Starting fastapi-pip-pap server ...")

    import uvicorn
    uvicorn.run("gemini-pip-pap:app", host=args.servername, port=int(args.port), reload=True)
