import os

import configargparse

from studip_parser import StudIpCrawler

if __name__ == '__main__':

    p = configargparse.ArgParser(default_config_files=['./config.yaml'], ignore_unknown_config_file_keys=True)

    p.add_argument('-s', '--single_link', help="Stud.IP Link to module overview")
    p.add_argument('-t', '--target', choices=['nextcloud', 'filesystem'], required=True,
                   help="Remote folder on nextcloud instance")
    p.add_argument('-o', '--output', default="./out", help="Directory to download files to")
    p.add_argument('-v', '--verbose', action="store_true")

    p.add_argument('--nextcloud_url')
    p.add_argument('--nextcloud_user')
    p.add_argument('--nextcloud_password')

    p.add_argument('--studip_url', required=True, help='Base URL to Stud.IP')
    p.add_argument('--studip_user', required=True, help='username for Stud.IP')
    p.add_argument('--studip_password', required=True, help='password for Stud.IP')

    args = p.parse_args()

    # Parse module list separately as it doesn't seem supported by the arg-parse-library
    modules = []
    try:
        with open("config.yaml") as config_file:
            modules = yaml.safe_load(config_file)
    except:
        pass

        # Create session
        crawler = StudIpCrawler(args)
        crawler.login_session()

    if args.target == "filesystem":
        # Sync module to local folder

        for file in files:
            folder_path = os.path.join(args.output, *file.relative_path.split("/"))
            file_path = os.path.join(folder_path, file.name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            if args.verbose:
                print("Download: ", file_path)

            with open(file_path, "wb") as local_file:
                local_file.write(crawler.download_file(file))

        # Fetch announcements
        announcements = crawler.download_announcements(args.single_link)

        if args.verbose:
            for anc in announcements:
                print("Announcement: ", anc.title)

        with open(os.path.join(args.output, "Ankündigungen.md"), "w") as local_file:
            local_file.write("\n\n\n".join([a.format_markdown() for a in announcements]))

        crawler.logout_session()

    elif args.target == "nextcloud":
        # Sync module to nextcloud
        pass
