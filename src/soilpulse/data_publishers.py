import requests
from .resource_management import Publisher, PublisherFactory
from .exceptions import DOIdataRetrievalException

class ZenodoPublisher(Publisher):
    key = "Zenodo"
    name = "Zenodo"

    def __init__(self, zenodo_id):
        self.zenodoID = zenodo_id

    def getFileInfo(self):
        """
        Collect resource files information from Zenodo record

        :param zenodo_id: Zenodo record identifier
        :return: dictionary of file info [{filename: name of the file, id: file id, size: file size, checksum: checksum, source_url: download link, local_path: path to local copy}, ...]
        """

        try:
            response = requests.get("https://zenodo.org/api/records/" + self.zenodoID).json()

        except requests.exceptions.ConnectionError:
            print("A connection error occurred. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        else:

            URLroot = response['links']['files']
            if isinstance(response['files'], list):
                allFilesInfo = []
                for i in range(0, len(response['files'])):
                    fileinfo = {}
                    filename = response['files'][i]['key']
                    id = response['files'][i]['id']
                    size = response['files'][i]['size']
                    checksum = response['files'][i]['checksum']
                    source_url = URLroot +"/" +filename
                    fileinfo.update \
                        ({'filename': filename, 'id': id, 'size': size, 'checksum': checksum, 'source_url': source_url, 'local_path': None})

                    allFilesInfo.append(fileinfo)
                return allFilesInfo
            else:
                raise DOIdataRetrievalException(
                    "Dataset files can not be retrieved - incorrect response structure.")
                return None
    def getMetadata(self):
        """
        Collect metadata package from Zenodo record

        :param zenodo_id: Zenodo record identifier
        :return: response as JSON
        """

        try:
            response = requests.get("https://zenodo.org/api/records/" + self.zenodoID).json()

        except requests.exceptions.ConnectionError:
            print("A connection error occurred. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        else:
            return response


PublisherFactory.registerPublisher(ZenodoPublisher, ZenodoPublisher.key)