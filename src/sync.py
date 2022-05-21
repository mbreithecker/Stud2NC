import os

from studip_parser import StudIpCrawler
from nextcloud import NextcloudClient

# All announcements for a given module are stored in this file
ANNOUNCEMENTS_FILE_NAME = "_Ankündigungen.md"


class NextcloudSync:

    __file_db_name = "sz_file_db.txt"
    __announcements_db_name = "sz_anc_db.txt"

    def __init__(self, args):
        self.args = args
        self.client: NextcloudClient = None
        self.crawler = None

        # Keeps track of existing files in the nextcloud
        self.__file_db = []
        self.__announcements_db = []

    def open(self):
        self.crawler = StudIpCrawler(self.args)
        self.crawler.login_session()

        self.client = NextcloudClient(self.args)

        file_db_txt = self.client.download_file(self.__file_db_name)
        if file_db_txt is not None:
            self.__file_db = [f for f in file_db_txt.text.strip().split("\n") if len(f) > 1]

        anc_db_txt = self.client.download_file(self.__announcements_db_name)
        if anc_db_txt is not None:
            self.__announcements_db = [f for f in anc_db_txt.text.strip().split("\n") if len(f) > 1]

        if self.args.verbose:
            print("Nextcloud database loaded")

    def close(self):
        # Upload database
        upload_db = "\n".join([str(entry) for entry in self.__file_db]).encode("utf-8")
        self.client.upload_file(upload_db, self.__file_db_name)

        upload_db = "\n".join([str(entry) for entry in self.__announcements_db]).encode("utf-8")
        self.client.upload_file(upload_db, self.__announcements_db_name)

        # Logout from Stud.IP
        self.crawler.logout_session()

    def sync_module(self, remote_url, destination):
        # Parse URL
        destination = destination if destination.endswith("/") else destination + "/"

        # Fetch all files
        files = self.crawler.find(remote_url.replace("overview", "files"))

        for file in files:
            if file.download_url not in self.__file_db:
                self.__file_db.append(file.download_url)

                if self.args.verbose:
                    print("Download: ", file.file_path())

                self.client.upload_file(self.crawler.download_file(file), destination + file.file_path())

        # Fetch announcements
        announcements = self.crawler.download_announcements(remote_url)

        remote_announcements = self.client.download_file(destination + ANNOUNCEMENTS_FILE_NAME) or ""
        if remote_announcements != "":
            remote_announcements = remote_announcements.text

        for anc in announcements:
            if anc.get_hash() not in self.__announcements_db:
                self.__announcements_db.append(anc.get_hash())

                remote_announcements = anc.format_markdown() + remote_announcements

                if self.args.verbose:
                    print("Announcement: " + anc.title)

        self.client.upload_file(remote_announcements.encode("utf-8"), destination + ANNOUNCEMENTS_FILE_NAME)


class FilesystemSync:
    """
    Not really a sync as it just overwrites everything.
    But if it should be a sync it would be implemented here
    """

    def __init__(self, args):
        self.args = args
        self.crawler: StudIpCrawler = None

    def open(self):
        self.crawler = StudIpCrawler(self.args)
        self.crawler.login_session()

    def close(self):
        self.crawler.logout_session()

    def sync_module(self, remote_url, destination):
        """
        Downloads all files and announcements from the given $remote_url
        and saves them to $destination
        :return:
        """
        # Fetch all files
        files = self.crawler.find(remote_url.replace("overview", "files"))

        for file in files:
            folder_path = os.path.join(destination, *file.relative_path.split("/"))
            file_path = os.path.join(folder_path, file.name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            if self.args.verbose:
                print("Download: ", file_path)

            with open(file_path, "wb") as local_file:
                local_file.write(self.crawler.download_file(file))

        # Fetch announcements
        announcements = self.crawler.download_announcements(remote_url)

        if self.args.verbose:
            for anc in announcements:
                print("Announcement: ", anc.title)

        with open(os.path.join(destination, ANNOUNCEMENTS_FILE_NAME), "w") as local_file:
            local_file.write("\n\n\n".join([a.format_markdown() for a in announcements]))
