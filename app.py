from flask import Flask, request, render_template, jsonify
from azure.storage.blob import BlobServiceClient
import logging
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs; use INFO or WARNING for less verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file named 'app.log'
        logging.StreamHandler()         # Log to the console
    ]
)
logger = logging.getLogger(__name__)


AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRINGONE")
CONTAINER_NAME = os.getenv("CONTAINER_NAMEone")  # Updated container name
UPLOAD_PATH = os.getenv("UPLOAD_PATHONE") # Updated directory path inside the container


# Blob service client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


@app.route("/")
def index():
    """
    Serve the HTML front end.
    """
    logger.info("Serving the index.html file")
    return render_template("index.html")


@app.route("/upload-files", methods=["POST"])
def upload_files():
    """
    Upload three files (two txt and one xml) to ADLS in the specified directory.
    """
    logger.info("Received a request to upload files")
    if "file1" not in request.files or "file2" not in request.files or "file3" not in request.files:
        logger.warning("Missing one or more files in the request")
        return jsonify({"status": "error", "message": "Please upload all three files"}), 400

    file1 = request.files["file1"]
    file2 = request.files["file2"]
    file3 = request.files["file3"]

    # Validate file types
    if not (file1.filename.endswith(".txt") and file2.filename.endswith(".txt") and file3.filename.endswith(".xml")):
        logger.warning("Invalid file types provided")
        return jsonify({"status": "error", "message": "File types must be 2 .txt and 1 .xml"}), 400

    # Upload files to ADLS
    try:
        files = [file1, file2, file3]
        for file in files:
            # Create the blob client with the specified path
            blob_name = f"{UPLOAD_PATH}/{file.filename}"  # Include the directory path
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
            # Upload the file
            logger.info(f"Uploading file {file.filename} to {blob_name}")
            blob_client.upload_blob(file.read(), overwrite=True)

        logger.info("All files uploaded successfully")
        return jsonify({"status": "success", "message": "Files uploaded successfully"}), 200
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Error uploading files: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
