import os
import sys
import logging
import coloredlogs
import argparse
import yaml
import hashlib
import requests
import jwcrypto.jwk as jwk
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from tempfile import NamedTemporaryFile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from jwcrypto import jwk, jwt
import tarfile
import json
import io
import time

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
        return f"{self.github_repo}/opa-bundles/{self.application}/{self.label}/{self.filename}"

    def download_bundle(self):
        """Download the bundle from GitHub."""
        response = requests.get(self.bundle_url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        temp_file = NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            f.write(response.content)
        
        return temp_file.name

    def get_etag(self, file_path):
        """Calculates the ETag header value based on the file content hash."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        etag = hasher.hexdigest()
        return etag

    def calculate_hash(self, file_content, algorithm='SHA-256'):
        """Calculate the hash of the file content."""
        hasher = hashlib.new(algorithm.lower().replace("-", ""))
        hasher.update(file_content)
        return hasher.hexdigest()

    def sign_bundle(self, file_hashes, private_key):
        """Signs the bundle using the given private key."""
        claims = {
            "files": file_hashes,
            "iat": int(time.time()),
            "iss": "JWTSercice"
        }
        
        header = {
            "alg": "ES256",
            "typ": "JWT",
            "kid": "myPublicKey"
        }

        token = jwt.JWT(header=header, claims=claims)
        token.make_signed_token(private_key)
        return token.serialize()

    def create_signed_tarball(self, original_bundle_file, signature):
        """Creates a new tarball including the original files and the signature."""
        signed_bundle_file = NamedTemporaryFile(delete=False)
        
        with tarfile.open(original_bundle_file, "r:gz") as tar:
            with tarfile.open(signed_bundle_file.name, "w:gz") as signed_tar:
                for member in tar.getmembers():
                    file_data = tar.extractfile(member).read()
                    tarinfo = tarfile.TarInfo(name=member.name)
                    tarinfo.size = len(file_data)
                    signed_tar.addfile(tarinfo, fileobj=io.BytesIO(file_data))

                # Add signature file
                signature_info = tarfile.TarInfo(name=".signatures.json")
                signature_info.size = len(signature)
                signed_tar.addfile(signature_info, io.BytesIO(signature.encode()))

        return signed_bundle_file.name

def generate_keys():
    """Generate a new ECC key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

#def get_jwks(public_key):
#    """Generate a JWKS representation of the given public key."""
    # Create a JWK object from ECC public key
    #jwk_key = jwk.JWK()
    #jwk_key.import_key(public_key)
    
    # Create a JWKSet containing the JWK object
    #jwks = jwk.JWKSet(keys=[jwk_key])
    
    # Export the JWKS as JSON string
    #return jwks.export(private_keys=False)

#private_key, public_key = generate_keys()
#jwks = get_jwks(public_key)

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

    try:
        bundle_file = bundle.download_bundle()
    except HTTPException as e:
        # Handle HTTP errors from download
        raise e

    if bundle_file is None:
        # Handle scenario where download_bundle() did not return a valid file path
        raise HTTPException(status_code=500, detail="Failed to download bundle")

    # Calculate ETag header value
    etag = bundle.get_etag(bundle_file)

    if if_none_match == etag:
        return Response(status_code=304)

    # Extract files and calculate their hashes
    file_hashes = []
    with tarfile.open(bundle_file, "r:gz") as tar:
        for member in tar.getmembers():
            file_data = tar.extractfile(member).read()
            file_hash = bundle.calculate_hash(file_data)
            file_hashes.append({
                "name": member.name,
                "hash": file_hash,
                "algorithm": "SHA-256"
            })

    # Sign the bundle
    signature = bundle.sign_bundle(file_hashes, private_key)

    # Create a new tarball including the original files and the signature
    signed_bundle_file = bundle.create_signed_tarball(bundle_file, signature)

    # Add Content-Disposition header
    response = FileResponse(signed_bundle_file, media_type="application/gzip", headers={
        "ETag": etag,
        "Content-Disposition": f"attachment; filename={filename}"
    })

    # Clean up the temporary files after sending the response
    if bundle_file:
        response.background = lambda: os.remove(bundle_file)
    if signed_bundle_file:
        response.background = lambda: os.remove(signed_bundle_file)

    return response

#@app.get("/jwks")
#async def get_jwks_endpoint():
#    """Serve the JWKS."""
#    return JSONResponse(content=jwks)

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
