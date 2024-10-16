import os
import random

from flask import Blueprint
from flask import send_from_directory

from src.logger import init_logger
from src.utils import products_upload_folder, load_files_in_folder

images_route = Blueprint('image', __name__)
documents_logger = init_logger('documents_logger')


@images_route.get('/documents/<string:category_id>/image.png', defaults={'product_id': None})
@images_route.get('/documents/<string:category_id>/<string:product_id>/image.jpg')
async def display_images(category_id: str, product_id: str | None = None):
    """
        allows employees to download claims documents
    :param product_id:
    :param category_id:
    :param user:
    :return:
    """
    file_path = products_upload_folder(category_id=category_id, product_id=product_id)
    files = load_files_in_folder(folder_path=file_path)
    documents_logger.info(f"Looking for products images in {file_path}")
    if not files:
        documents_logger.info("Product Images not found here: {}")
        return {"message": "No documents found for this product."}, 404
    documents_logger.info(f"found in display images files: {files}")
    # Randomly select one file
    selected_file = random.choice(files)
    filename = os.path.basename(selected_file)

    documents_logger.info(f"selected file: {selected_file}")
    # Serve the selected file
    return send_from_directory(directory=file_path, path=filename)
