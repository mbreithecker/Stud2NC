import requests


class NextcloudClient:
    """
    Handles session and file upload to nextcloud
    """

    __nc_headers = {'Accept': '*/*'}

    def __init__(self, args):
        self.base_url = args.nextcloud_url
        self.base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"
        self.user = args.nextcloud_user
        self.password = args.nextcloud_password
        self.args = args

    def upload_file(self, binary_content, destination: str):

        # Create nextcloud directory
        build_path = ""
        for line in destination.split("/")[0:-1]:
            build_path = build_path + line + "/"
            requests.request('MKCOL', self.base_url + build_path, headers=self.__nc_headers,
                             auth=(self.user, self.password))

        # Upload file
        req_up = requests.request('PUT', self.base_url + destination,
                                  data=binary_content, headers=self.__nc_headers,
                                  auth=(self.user, self.password))

        if req_up.status_code == 201 or req_up.status_code == 204:
            if self.args.verbose:
                print("Uploaded: " + destination)
        else:
            print("Error uploading file to nextcloud: " + destination)

    def download_file(self, remote_file) -> requests.Response:
        response = requests.request('GET', self.base_url + remote_file, headers=self.__nc_headers,
                                    auth=(self.user, self.password))
        if response.status_code != 200:
            print("Error downloading file: " + remote_file)
            return None
        else:
            return response
