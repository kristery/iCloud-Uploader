# iCloud Uploader

This script is an automated uploader to iCloud. It monitors a specified directory for any new files and automatically uploads them to the designated iCloud Drive folder. The script categorizes files into images, videos, and others based on their extensions and uploads them to the corresponding subfolders in iCloud Drive.

The script also handles two-factor authentication and two-step verification for iCloud. It prompts the user for verification codes when needed.

## Prerequisites

- Python 3.6 or newer
- pyicloud library
- click library

The script depends on the pyicloud library to interact with iCloud and the click library for user-friendly command-line interfaces. You can install these libraries using pip:
```
pip install pyicloud click
```
## How to Execute

1. Prepare an info file. The script reads username, password, and iCloud Drive folder name from a file. Each piece of information should be on its own line in the file. By default, the script reads from a file named info.txt in the same directory, but you can specify a different file using the -f or --file command-line option.

Example info.txt:

```
username@example.com
password123
my_folder
```

2. Run the script. If you are using the default info file, you can simply run:
```
cd src
python icloud_uploader.py
```

If you want to specify a different info file, use the -f or --file option:

```
cd src
python icloud_uploader.py -f my_info.txt
```

## Notes

- The script monitors the current working directory. Any new files in this directory, excluding Python files, are uploaded to iCloud.
- If a new directory appears in the monitored directory, the script compresses it into a zip file and uploads it.
- The script creates the iCloud Drive folder if it does not exist. It also creates images, videos, and files subfolders in the iCloud Drive folder.
- The script checks the monitored directory every minute for new files.
