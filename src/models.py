import hashlib
import re


class Announcement:
    """
    Represents a Stud.IP announcement in a given module
    """
    def __init__(self):
        self.title: str = ""
        self.date: str = ""
        self.content: str = ""
        self.remote_link: str = ""

    def format_markdown(self):
        """
        Replace html tags with Markdown formatting
        :return: string of contents with Markdown formatting
        """
        formatted_content = self.content
        formatted_content = formatted_content.replace("<strong>", "**").replace("</strong>", "**")
        formatted_content = formatted_content.replace("<small>", "").replace("</small>", "")
        formatted_content = formatted_content.replace("<br/>", "\n\n")
        formatted_content = formatted_content.replace('<div class="formatted-content">', "")
        formatted_content = formatted_content.replace('</div>', "")

        # Extract links
        pattern = re.compile(r'(<a\s+(?:[^>]*?\s+)?href=)(["\'])(.*?)\2(.*>)')

        for (start, quote, link, end) in re.findall(pattern, formatted_content):
            str_to_replace = start + quote + link + quote + end
            str_replacement = "<" + link + ">"
            formatted_content = formatted_content.replace(str_to_replace, str_replacement)

        formatted_announcement = "#### " + self.title + "\n\n"
        formatted_announcement += "> " + self.date + "\n\n"
        formatted_announcement += formatted_content + "\n\n"

        return formatted_announcement

    def get_hash(self):
        """
        Returns hash of the announcement, needed to check for duplicated
        :return: hash
        """
        text_to_hash = "-#-".join([self.title, self.date, self.content])
        return hashlib.sha256(text_to_hash.encode("utf-8")).hexdigest()


class RemoteFile:
    """
    Represents a remote file in Stud.IP
    """
    base_url: str = None
    id: str = None
    name: str = None
    details_url = None
    download_url = None
    relative_path = None
