import configargparse
import yaml

from sync import FilesystemSync

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

    # Start program

    if args.target == "filesystem":
        # Sync module to local folder

        fileSync = FilesystemSync(args)
        fileSync.open()

        if args.single_link:
            if args.verbose:
                print("Sync single module: " + args.single_link)

            fileSync.sync_module(args.single_link, args.output)
        else:
            for module in modules:
                if args.verbose:
                    print("Sync module: " + module)

                fileSync.sync_module(module.module_link, module.destination)

        fileSync.close()

    elif args.target == "nextcloud":
        # Sync module to nextcloud
        pass
