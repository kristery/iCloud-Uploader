import argparse
import os
import sys
import time
import zipfile

from pyicloud import PyiCloudService


def read_info(file_path):
    # Read the file and extract the information
    with open(file_path, "r") as file:
        lines = file.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
        folder = lines[2].strip()

    return username, password, folder


def login(username, password):
    # Now you can use the username and password to login
    api = PyiCloudService(username, password)

    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input(
            "Enter the code you received of one of your approved devices: "
        )
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print(
                    "Failed to request trust. You will likely be prompted for the code again in the coming weeks"
                )
    elif api.requires_2sa:
        import click

        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s"
                % (
                    i,
                    device.get(
                        "deviceName", "SMS to %s" % device.get("phoneNumber")
                    ),
                )
            )

        device = click.prompt("Which device would you like to use?", default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt("Please enter validation code")
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)
    api.drive.params["clientId"] = api.client_id
    return api


def is_dir(drive, folder):  # drive: api.drive, api.drive["folder"]...
    if drive[folder].dir() is None:
        return False
    return True


def build_folder_structure(api, icloud_folder, username, password):
    # check if folder exists in iCloud Drive
    if icloud_folder in api.drive.dir():
        print(f"Folder {icloud_folder} already exists in iCloud Drive")
        if is_dir(api.drive, icloud_folder):
            print(f"Folder {icloud_folder} is a directory")
        else:
            print(
                f"{icloud_folder} exists and it is not a directory. Please use another folder name"
            )
            sys.exit(1)
    else:
        api._drive.params["clientId"] = api.client_id
        api.drive.mkdir(icloud_folder)
        print(f"Created folder {icloud_folder} in iCloud Drive")
        api = login(username, password)  # refresh api

    api._drive.params["clientId"] = api.client_id
    api.drive[icloud_folder].mkdir("images")
    api.drive[icloud_folder].mkdir("videos")
    api.drive[icloud_folder].mkdir("files")
    api = login(username, password)  # refresh api

    print("Created subfolders in iCloud Drive")
    print("Ready to upload files")
    return api


def main(args):
    username, password, icloud_folder = read_info(args.file)

    folder_path = "./"
    file_list = os.listdir(folder_path)
    api = PyiCloudService(username, password)

    api = build_folder_structure(api, icloud_folder, username, password)

    image_extensions = ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "ico"]
    video_extensions = ["mp4", "avi", "mkv", "flv", "mov", "wmv"]

    initial = True

    while True:
        # print("Checking files...")
        current_file_list = os.listdir(folder_path)
        new_files = set(current_file_list) - set(file_list)
        if len(new_files) > 0:
            print(f"new files: {new_files}")
        for filename in new_files:
            if (
                not filename.endswith(".py")
                and "crdownload" not in filename
                and not initial
            ):
                print(f"uploading {filename}")

                if os.path.isdir(filename):
                    # Compress directory to zip file and upload
                    zip_filename = f"{filename}.zip"
                    with zipfile.ZipFile(
                        zip_filename, "w", zipfile.ZIP_DEFLATED
                    ) as zipf:
                        for root, dirs, files in os.walk(filename):
                            for file in files:
                                zipf.write(os.path.join(root, file))

                    with open(zip_filename, "rb") as fp:
                        try:
                            api.drive[icloud_folder]["files"].upload(fp)
                            print("upload zip file successfully")
                        except Exception as e:
                            print("Error:", e)

                    # Remove the zip file after uploading
                    os.remove(zip_filename)

                else:
                    with open(filename, "rb") as fp:
                        try:
                            extension = filename.split(".")[-1]
                            if extension.lower() in image_extensions:
                                target_folder = "images"
                                print(
                                    f"files identified as image, uploading to {target_folder}"
                                )
                            elif extension.lower() in video_extensions:
                                target_folder = "videos"
                                print(
                                    f"files identified as video, uploading to {target_folder}"
                                )
                            else:
                                target_folder = "files"
                                print(
                                    f"files identified as other, uploading to {target_folder}"
                                )

                            api.drive[icloud_folder][target_folder].upload(fp)
                            print("upload successfully")
                        except Exception as e:
                            print("Error:", e)

        file_list = current_file_list
        initial = False
        time.sleep(1 * 10)  # wait for 1 minutes before checking again


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read username, password, and folder name from a file"
    )
    parser.add_argument(
        "-f",
        "--file",
        default="info.txt",
        help="Input file (default: info.txt)",
    )
    args = parser.parse_args()
    main(args)
