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

### Installation
```
zip Stud2NC src/*
python3 Stud2NC.zip [args]
```

### Local sync to file-system
The easiest way to fetch files, is to just download them to 
a local directory. However, this method does not check if
the file has already been downloaded before.

If you just want to fetch a module with all files and 
announcements to your disk use:

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


### Configure multiple modules to sync


### Contribution
By creating a pull request you accept that the code is licenced under the conditions specified in the LICENSE.txt file.