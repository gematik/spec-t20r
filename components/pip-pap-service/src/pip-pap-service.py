import sys
import signal
import logging
import argparse
import yaml
import os
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)


class Bundles:
    """Class to handle PIP and PAP bundles."""

    def __init__(self, bundle_storage_path, application, version, bundle_type):
        """Initialize Bundles object with application, version, and bundle type."""
        self.bundle_storage_path = bundle_storage_path
        self.application = application
        self.version = version
        self.bundle_type = bundle_type

    def get_bundle_path(self):
        """Generate file path for the bundle."""
        # Construct the file path using the base path and the values of application, version, and bundleType
        return os.path.join(
            self.bundle_storage_path,
            self.application,
            self.version,
            self.bundle_type,
            "bundle.tar.gz",
        )

    def get_bundle_revision(self):
        """Generate ETag for the bundle."""
        return os.path.getmtime(self.get_bundle_path())


# Define routes for PIP and PAP bundles
@app.route("/<application>/<version>/<bundleType>/bundle.tar.gz", methods=["GET"])
def get_bundle(application, version, bundleType):
    """Retrieve a signed PIP or PAP OPA bundle file.

    Args:
        application (str): The name of the application.
        version (str): The version of the application.
        bundleType (str): The type of bundle (pip or pap).
        config (dict): Configuration settings.

    Returns:
        file: The signed OPA bundle file.

    Raises:
        HTTPException: If an invalid bundle type is provided or the bundle file does not exist.

    """
    logger = logging.getLogger("pip-pap-service")

    # Accessing request headers
    headers = request.headers
    logger.debug(f"Request headers: {headers}")

    # Validate bundleType
    if bundleType not in ["pip", "pap"]:
        return jsonify({"error": "Invalid bundle type"}), 400

    # Create a Bundles object
    bundle = Bundles(
        app.config["bundle_storage_path"], application, version, bundleType
    )
    bundle_path = bundle.get_bundle_path()

    # Handle 404 Not Found error
    if not os.path.exists(bundle_path):
        logger.debug(f"The requested bundle does not exist: {bundle_path}")
        return jsonify({"error": "The requested bundle does not exist."}), 404

    # Generate ETag for the bundle
    etag = bundle.get_bundle_revision()

    # Check If-None-Match header
    if request.headers.get("If-None-Match") == str(etag):
        logger.debug(f"ETag matches for {bundle_path}. Returning 304 Not Modified.")
        return "", 304  # Return 304 Not Modified if ETag matches

    # Return the file as an attachment with ETag header
    logger.debug(f"Returning {bundle_path} with ETag: {etag}")
    return send_file(
        bundle_path, as_attachment=True, mimetype="application/gzip", etag=etag
    )


def load_config(filename):
    """
    Loads configuration from a YAML file.
    Args:
        filename (str): The path to the YAML configuration file.
    Returns:
        dict: The configuration settings.
    """
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
    return config


def setup_logging(log_config):
    """
    Setup logging configuration.
    Args:
        log_config (dict): Logging configuration.
    Configuration:
        # loglevel is one of CRITICAL, ERROR, WARNING, INFO, DEBUG
        loglevel: "DEBUG"
        log_to_console: True
        log _to_file: True
        logfile: "tsp-cli.log"
    Returns:
        logging.Logger: Logger object.
    """
    logger = logging.getLogger("pip-pap-service")
    match log_config["loglevel"].upper():
        case "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        case "ERROR":
            logger.setLevel(logging.ERROR)
        case "WARNING":
            logger.setLevel(logging.WARNING)
        case "DEBUG":
            logger.setLevel(logging.DEBUG)
        case _:
            logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s.%(levelname)s %(lineno)d]: %(message)s"
    )
    if log_config["log_to_console"]:
        # Create a stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    if log_config["log_to_file"]:
        # Create a file handler
        file_handler = logging.FileHandler(f"{log_config['service_name']}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def sigterm_handler(signal, frame):
    """
    Handle SIGTERM signal.
    (for docker stop support)
    """
    logger = logging.getLogger("pip-pap-service")
    logger.info(f"{signal} received. Exiting...")
    sys.exit(0)


def interrupt_handler(signum, frame):
    logger = logging.getLogger("pip-pap-service")
    logger.info(f"{signal} received. Exiting...")
    sys.exit(0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="mailrobot for automatic email testing."
    )
    parser.add_argument(
        "--configfile", default="config.yaml", help="The configfile for tsp-cli."
    )
    args = parser.parse_args()

    config = load_config(args.configfile)
    logger = setup_logging(config["logging"])

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, interrupt_handler)

    app.config.update(config)  # Update app config with loaded configuration settings
    logger.info("Starting pip-pap-service...")
    logger.debug(f"Configuration: {config}")
    app.run(debug=False)

else:
    config = load_config("config.yaml")
    logger = setup_logging(config["logging"])

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, interrupt_handler)

    app.config.update(config)  # Update app config with loaded configuration settings
    logger.info("Starting pip-pap-service...")
    logger.debug(f"Configuration: {config}")
