#!/usr/bin/env python
import argparse
import csv
import os
import subprocess
from string import Template

GOOGLE_FORMAT = ["name", "url", "username", "password"]

TEMPLATE_INFOS = "$password\ncomment:\nurl: $url\nusername: $username"

TEMP_FILE = "tmp.txt"


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="import", description="Import tools for Gopass."
    )
    parser.add_argument(
        "--csv",
        help="Path of the csv file.",
        required=True,
        default="./Chrome Passwords.csv",
    )
    return parser.parse_args()


def extract_infos(row: dict) -> (str, str, str, str):
    name = row["name"]
    if not name:
        return None, None, None, None
    url = row["url"]
    username = row["username"]
    password = row["password"]
    if not username:
        print(f"Be careful, no username for {name}")
    secret_path = f"websites/{name}/{username}"
    return secret_path, url, username, password


def generate_template(url, username, password):
    d = dict(password=password, url=url, username=username)
    return Template(TEMPLATE_INFOS).substitute(d)


def get_cmd(infos, secret_path):
    with open(TEMP_FILE, "w") as f:
        f.write(infos)
    return f"cat {TEMP_FILE} | gopass insert -f {secret_path}"


def execute_cmd(cmd, secret_path):
    exitcode, output_insert = subprocess.getstatusoutput(cmd)
    if not exitcode and output_insert:
        print("insert secret: ", secret_path)
    else:
        print("Error while insert secret: ", secret_path, "\n", cmd)


def read_csv(args_parsed: argparse.Namespace):
    with open(args_parsed.csv, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            secret_path, url, username, password = extract_infos(row)
            if secret_path:
                infos = generate_template(url, username, password)
                cmd = get_cmd(infos, secret_path)
                execute_cmd(cmd, secret_path)
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)


def import_from_csv(args_parsed: argparse.Namespace):
    read_csv(args_parsed)


def main(args_parsed: argparse.Namespace) -> None:
    import_from_csv(args_parsed)


if __name__ == "__main__":
    args = get_args()
    main(args)
