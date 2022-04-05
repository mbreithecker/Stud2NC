import requests

from models import RemoteFile, Announcement


class NextcloudClient:
    """
    Handles session and file upload to nextcloud
    """

    __file_db_name = "sz_file_db.txt"
    __announcements_db_name = "sz_anc_db.tx"
    __nc_headers = {'Accept': '*/*'}

    def __init__(self, args):
        self.base_url = args.nextcloud_url
        self.base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"
        self.user = args.nextcloud_user
        self.password = args.nextcloud_password
        self.args = args

        # Keeps track of existing files in the nextcloud
        self.__file_db = []
        self.__announcements_db = []

    def login_session(self):
        file_db_txt = requests.request('GET', self.base_url + "sz_file_db.txt",
                                       headers=self.__nc_headers,
                                       auth=(self.user, self.password))

        for entry in file_db_txt.text.strip().split("\n"):
            self.__file_db.append(entry)

        anc_db_txt = requests.request('GET', self.base_url + "sz_anc_db.txt",
                                      headers=self.__nc_headers,
                                      auth=(self.user, self.password))

        for entry in anc_db_txt.text.strip().split("\n"):
            self.__announcements_db.append(entry)

        print("Database loaded")

    def logout_session(self):
        upload_db = "\n".join([str(entry) for entry in self.__file_db]).encode("utf-8")
        req_up_file = requests.request('PUT', self.base_url + "sz_file_db.txt",
                                       data=upload_db, headers=self.__nc_headers, auth=(self.user, self.password))

        if req_up_file.status_code != 200:
            print("Error storing database: file-db")

        upload_db = "\n".join([str(entry) for entry in self.__announcements_db]).encode("utf-8")
        req_up_anc = requests.request('PUT', self.base_url + "sz_anc_db.txt", data=upload_db, headers=self.__nc_headers,
                                      auth=(self.user, self.password))

        if req_up_anc.status_code != 200:
            print("Error storing database: announcements-db")

        if req_up_file.status_code == 200 and req_up_anc.status_code == 200:
            print("Database stored")

    def upload_file(self, remote_file: RemoteFile, binary_content, destination_path: str):

        destination_path = destination_path if destination_path.endswith("/") else destination_path + "/"
        destination_path += remote_file.relative_path
        # Create nextcloud directory
        build_path = ""
        for line in destination_path.split("/"):
            build_path = build_path + line + "/"
            requests.request('MKCOL', self.base_url + build_path, headers=self.__nc_headers,
                             auth=(self.user, self.password))

        req_up = requests.request('PUT', self.base_url + destination_path + "/" + remote_file.name,
                                  data=binary_content, headers=self.__nc_headers,
                                  auth=(self.user, self.password))

        if req_up.status_code == 200:
            if self.args.verbose:
                print("Uploaded: " + destination_path + "/" + remote_file.name)
        else:
            print("Error uploading file to nextcloud: " + destination_path + "/" + remote_file.name)

    def download_file(self, remote_file):
        announcement_response = requests.request('GET', self.base_url + remote_file,
                                                 headers=self.__nc_headers,
                                                 auth=(self.user, self.password))
        if announcement_response.status_code != 200:
            print("Error downloading file: " + remote_file)
            return None
        else:
            return announcement_response

    def add_file_to_db(self, remote_file: RemoteFile):
        if not self.does_file_exist(remote_file):
            self.__file_db.append(remote_file.download_url)

    def does_file_exist(self, remote_file: RemoteFile):
        return self.__file_db.index(remote_file.download_url) != -1

    def add_announcement_to_db(self, announcement: Announcement):
        if not self.does_announcement_exist(announcement):
            self.__announcements_db.append(announcement.get_hash())

    def does_announcement_exist(self, announcement: Announcement):
        return self.__announcements_db.index(announcement.get_hash()) != -1
