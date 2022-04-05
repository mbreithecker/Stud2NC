import json
from typing import List

import requests
from bs4 import BeautifulSoup

from models import RemoteFile, Announcement


class StudIpCrawler:
    """
    Creates a login session and parses the html to fetch files and announcements
    """

    def __init__(self, args):
        self.__session = None
        self.studip_user = args.studip_user
        self.studip_password = args.studip_password
        self.base_url = args.studip_url[:-1] if args.studip_url.endswith("/") else args.studip_url

    def login_session(self):
        """ Login in via the login-page and safe the session cookie """
        self.__session = requests.Session()

        login_page = self.__session.get(self.base_url)

        # "Security"...
        # Stuff that needs to be fetched and retransmitted to the endpoint
        security_token = BeautifulSoup(login_page.text, 'html.parser') \
            .form.find("input", {"name": "security_token"}).attrs["value"]
        login_ticket = BeautifulSoup(login_page.text, 'html.parser') \
            .form.find("input", {"name": "login_ticket"}).attrs["value"]
        resolution = BeautifulSoup(login_page.text, 'html.parser') \
            .form.find("input", {"name": "resolution"}).attrs["value"]
        device_pixel_ratio = BeautifulSoup(login_page.text, 'html.parser') \
            .form.find("input", {"name": "device_pixel_ratio"}).attrs["value"]

        login_data = {
            'loginname': self.studip_user,
            'password': self.studip_password,
            'security_token': security_token,
            'login_ticket': login_ticket,
            'resolution': resolution,
            'device_pixel_ratio': device_pixel_ratio
        }

        response = self.__session.post(self.base_url, data=login_data)
        if response.status_code == 200:
            print("Session created")
        else:
            print("Error: ", response)

    def logout_session(self):
        """ Gracefully close session """
        response = self.__session.get(self.base_url + "/" + 'logout.php')
        if response.status_code == 200:
            print("Session closed")
        else:
            print("Error: ", response)

    def __find(self, remote_link: str, path=""):
        """
        Recursively finds all files and folders on the given remote link
        :param path: used internally to keep track of recursive sub-folders traverse
        :param remote_link: Link to "Files" of a module
        :return: List of all file-names including (subfolders) which can be found at the given remote_link
        """

        if not remote_link.startswith(self.base_url):
            print("Error: Invalid link: ", remote_link)

        html_soup = BeautifulSoup(self.__session.get(remote_link).text, 'html.parser')

        # JavaScript is used to render some html but fortunately all the information is stored in a plain json-string
        json_files = json.loads(
            html_soup.find_all("form", {"data-breadcrumbs": True})[0].get('data-files').replace("\\/", "/"))
        json_folders = json.loads(
            html_soup.find_all("form", {"data-breadcrumbs": True})[0].get('data-folders').replace("\\/", "/"))

        files: [RemoteFile] = []

        for file in json_files:
            try:
                remote_file = RemoteFile()
                remote_file.id = file.get('id')
                remote_file.name = file.get('name')
                remote_file.details_url = file.get('details_url')
                remote_file.download_url = file.get('download_url')
                remote_file.relative_path = path

                files.append(remote_file)

            except Exception as e:
                print("Couldn't fetch file: ", e)

        for folder in json_folders:
            name = folder.get('name')
            url = folder.get('url')
            files += self.__find(url, path + "/" + name)

        return files

    def find(self, remote_link: str):
        """
        Recursively finds all files and folders on the given remote link
        :param remote_link: Link to "Files" of a module
        :return: List of all file-names including (subfolders) which can be found at the given remote_link
        """
        return self.__find(remote_link, path="")

    def download_file(self, remote_file: RemoteFile):
        """
        Downloads content of a remote file
        :param remote_file:
        :return: Returns the binary contents, can be directly written to a file or uploaded in a post request
        """
        response = self.__session.post(remote_file.download_url)
        if response.status_code == 200:
            return response.content

        return None

    def download_announcements(self, remote_link="") -> List[Announcement]:
        """
        Downloads all announcements for the given module
        :param remote_link: Link to the overview page of the module
        :return: List of all announcements for the module
        """

        if not remote_link.startswith(self.base_url):
            print("Error: Invalid link: ", remote_link)

        html_soup = BeautifulSoup(self.__session.get(remote_link).text, 'html.parser')

        announcements_list = list()
        for entry in html_soup.find_all(class_='studip'):
            if "Ankündigungen" in entry.header.h1.get_text():
                for article in entry.find_all("article", recursive=False):
                    announcement = Announcement()
                    announcement.title = article.h1.a.get_text().strip()
                    announcement.date = article.nav.span.get_text().strip()
                    announcement.content = str(article.section.article.div)
                    announcement.remote_link = remote_link

                    announcements_list.append(announcement)

        return announcements_list
