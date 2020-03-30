#!/usr/bin/env python
import argparse
import csv
import subprocess
from urllib.parse import urlparse

GOOGLE_FORMAT = ["name", "url", "username", "password"]
FILE_NAME = "secrets_from_gopass.csv"


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="export", description="Export tools for Gopass."
    )

    return parser.parse_args()


def extract_infos_from_path(path: str) -> (str, str):
    url = None
    elements = path.split("/")
    for element in elements:
        if "." in element:
            url_parsed = urlparse(element, allow_fragments=False)
            url = url_parsed.geturl()
            break
    username = elements[-1]
    return url, username


def extract_infos_from_show(infos: str) -> (str, str, str, str, bool):
    binary = False
    lines = infos.splitlines()
    password = lines[0]
    username = None
    url = None
    name = None
    for line in lines:
        if "user: " in line:
            username = line.replace("user: ", "")
        if "username: " in line:
            username = line.replace("username: ", "")
        if "url: " in line:
            url_parsed = urlparse(line.replace("url: ", ""), allow_fragments=False)
            url = url_parsed.geturl()
            name = url_parsed.hostname
    if len(lines) > 1 and (not username and not url):
        password = infos
        binary = True
    return name, url, username, password, binary


def get_infos(secret_path: str, output_show: str) -> (str, str, str, str, bool):
    url = ""
    url_path = None
    username_path = None
    name_show, url_show, username_show, password, binary = extract_infos_from_show(
        output_show
    )
    if not url_show or not username_show:
        url_path, username_path = extract_infos_from_path(secret_path)
    if url_show:
        url = url_show
    elif url_path:
        url = url_path
    if username_show:
        username = username_show
    else:
        username = username_path
    if name_show:
        name = name_show
    else:
        name = url
    return name, url, username, password, binary


def get_secrets_path() -> list:
    secrets_path = None
    exitcode, output_list = subprocess.getstatusoutput("gopass list -f")
    if not exitcode and output_list:
        secrets_path = output_list.splitlines()
    return secrets_path


def write_csv(format_header: list, secrets_path: list):
    with open(FILE_NAME, "w") as csv_file:
        fieldnames = format_header
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for secret_path in secrets_path:
            exitcode, output_show = subprocess.getstatusoutput(
                f"gopass show {secret_path}"
            )
            if not exitcode and output_show:
                name, url, username, password, binary = get_infos(
                    secret_path, output_show
                )
                if url and not binary:
                    writer.writerow(
                        {
                            "name": name,
                            "url": url,
                            "username": username,
                            "password": password,
                        }
                    )


def export_to_csv(args_parsed):
    secrets_path = get_secrets_path()
    write_csv(GOOGLE_FORMAT, secrets_path)


def main(args_parsed: argparse.Namespace) -> None:
    export_to_csv(args_parsed)


if __name__ == "__main__":
    args = get_args()
    main(args)
