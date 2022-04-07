import os

from studip_parser import StudIpCrawler
from nextcloud import NextcloudClient


class NextcloudSync:

    def __init__(self, args, crawler: StudIpCrawler):
        self.args = args
        self.client: NextcloudClient = None
        self.crawler = crawler
        self.__files_db = []
        self.__announcements_db = []

    def open(self):
        self.client = NextcloudClient(self.args)
        self.client.login_session()

        self.crawler.login_session()

    def close(self):
        # Upload database
        self.client.upload_file()

        self.client.logout_session()
        self.crawler.logout_session()

    def sync_module(self):
        pass
    #
    # def __add_file_to_db(self, remote_file: RemoteFile):
    #     if not self.does_file_exist(remote_file):
    #         self.__file_db.append(remote_file.download_url)
    #
    # def __does_file_exist(self, remote_file: RemoteFile):
    #     return self.__file_db.index(remote_file.download_url) != -1
    #
    # def __add_announcement_to_db(self, announcement: Announcement):
    #     if not self.does_announcement_exist(announcement):
    #         self.__announcements_db.append(announcement.get_hash())
    #
    # def __does_announcement_exist(self, announcement: Announcement):
    #     return self.__announcements_db.index(announcement.get_hash()) != -1


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

        with open(os.path.join(destination, "Ankündigungen.md"), "w") as local_file:
            local_file.write("\n\n\n".join([a.format_markdown() for a in announcements]))
