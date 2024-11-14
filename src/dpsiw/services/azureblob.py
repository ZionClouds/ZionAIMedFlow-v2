import logging
import os
from urllib.parse import urlparse
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import click

from dpsiw.services.settings import Settings, get_settings_instance


def get_blob_name(url: str) -> str | None:
    try:
        parsed_url = urlparse(url)
        blob_name = parsed_url.path.lstrip('/').split('/', 1)[1]
        return blob_name
    except Exception as e:
        logging.error(f'Unable to get the blob name: {e}')
        return None


def get_file_name_and_extension(url) -> tuple[str, str]:
    """
    Extracts the file name and extension from a given URL.

    Args:
    url (str): The URL containing the file.

    Returns:
    tuple: A tuple containing the file name and extension.
    """
    # Parse the URL to extract the path
    parsed_url = urlparse(url)

    # Extract the file name with extension from the path
    file_name_with_extension = parsed_url.path.split("/")[-1]

    # Split the file name and extension
    file_name, file_extension = file_name_with_extension.rsplit('.', 1)

    return file_name, '.' + file_extension


settings: Settings = get_settings_instance()


class AzureBlobContainer:
    """
    Helper class to manage an Azure Blob Container.
    """

    def __init__(self, container_name: str, blob_service_client: BlobServiceClient = None, ):
        self.blob_service_client = blob_service_client
        self.container_name = container_name

        if self.blob_service_client is None:
            self.blob_service_client = AzureBlobContainer.get_blob_service_client()

    @staticmethod
    def get_blob_service_client(account_url=settings.storage_url) -> BlobServiceClient:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url, credential=credential)
        return blob_service_client

    def create_container(self):
        try:
            self.blob_service_client.create_container(
                self.container_name)
            logging.info(f"Container created: {self.container_name}")
        except Exception as e:
            logging.error(f"Container creation failed: {e}")

    def upload_bytes(self, data: bytes, target_blob_path: str, overwrite: bool = True):
        click.echo("\nUploading bytes to Azure Blob Storage")
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=target_blob_path)
        blob_client.upload_blob(data, overwrite=overwrite)

    def upload_file(self, file_path: str, target_blob_path: str, overwrite: bool = True):
        click.echo(f"\nUploading {file_path} to Azure Blob Storage" +
                   target_blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=target_blob_path)
        with open(file=file_path, mode="rb") as data:
            blob_client.upload_blob(data, overwrite=overwrite)

    def download_blob(self, target_blob_path: str, file_path: str):
        click.echo(f"\nDownloading blob {target_blob_path} to {file_path}")
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=target_blob_path)
        with open(file=os.path.join(file_path, mode="wb")) as sample_blob:
            download_stream = blob_client.download_blob()

            sample_blob.write(download_stream.readall())

    def download_blob_url(self, url: str, file_path: str = None):
        # ROOT = '/home/alex/github/am8850/zebra/downloads/'
        # TODO: Add a check to see if the file already exists
        ROOT = ''
        target_blob_path = get_blob_name(url)
        if file_path is None:
            (file_name, file_ext) = get_file_name_and_extension(url)
            # id = str(uuid.uuid4())
            file_path = ROOT+file_name+file_ext
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=target_blob_path)
        click.echo(f"\nDownloading blob {target_blob_path} to {file_path}")
        try:
            with open(file_path, 'wb') as file:
                download_stream = blob_client.download_blob()
                file.write(download_stream.readall())
            return file_path
        except Exception as e:
            logging.error(f"Unable to write file: Error {e}")
            return None

    def list_blobs(self):
        click.echo("\nListing blobs...")
        container_client = self.blob_service_client.get_container_client(
            self.container_name)
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)

    def delete_blob(self, target_blob_path: str):
        click.echo("\nDeleting blob \n\t" + target_blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=target_blob_path)
        blob_client.delete_blob()

    def check_blob(self, url: str, container: str = 'medical-notes-in'):
        blob_name = get_blob_name(url)
        if blob_name is None:
            return False
        try:

            try:
                blob_client = self.blob_service_client.get_blob_client(
                    self.container_name,
                    blob_name)
                # Check if the blob exists
                blob_client.get_blob_properties()
                return True
            except Exception as e:
                logging.error(e)
                return False
        except:
            return False
