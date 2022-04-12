# Stud2NC
###### Version: 1.0.0 for Stud.IP v4.6.2.1

---
### Introduction
Stud2NC is a WebCrawler to download files from 
StudIp ([https://www.studip.de/](https://www.studip.de/)) 
and upload them to a Nextcloud instance (via WebDav)

I created this script to fetch my homework assignments, 
scripts, lecture information, etc. from Stud.IP during my 
time at university. I disliked the mobile interface and that it 
always required a internet connection. Also, I wanted to 
have my files on my phone and my laptop at the same time.

I used to run this script every 15 minutes on a VPS. 
It also supports Stud.IP-announcements. A nice thing about it is,
that it keeps the changelog of announcements. 
Lecturers usually tended to delete them after some time.
Since I'm no longer attending university I decided to polish the
source code a little and publish it on GitHub.

### Installation
```
cd src
zip ../Stud2NC.zip ./*
cd ..
python3 Stud2NC.zip [args]
```
Copy `Stud2NC.zip` and (the configured) `config.yaml` to a VPS and configure a
crontab (`crontab -e`):
```
*/15 * * * * python3 Stud2NC.zip
```

### Local sync to file-system
The easiest way to fetch files, is to just download them to 
a local directory. However, this method does not check if
the file has already been downloaded before. Therefore,
this is useful if you just want to fetch a module with all 
files & announcements and save it to your disk.

Enter the url and login credentials to the config.yaml
to avoid passing everything as command-line args.

```
python3 Stud2NC.zip -d filesystem -o [ModuleName] -s [link]
```

### Configuration
Configuration can be done via command-line, config-file 
or environment-variables. For example passwords can be 
injected via the environment whereas the folder configuration 
should be set in a config file.

The `config.yaml` in this project can be used as a template.
It is heavily commented. Replace all the credentials and 
specify the required modules.

### Contribution
By creating a pull request you accept that the code is 
licenced under the conditions specified in the LICENSE.txt file.

One thing I never really fixed, is when files get edited, but
don't change their file-id. Stud2NC won't resync them. 
When a file has changed the edit-date differs from the creation-date.
This makes it possible to check for edited files. Feel free to create
a pull request.