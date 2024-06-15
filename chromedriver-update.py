#!/usr/bin/env python3

import os
import shutil
import stat
import sys

import requests
import json
import zipfile

from contextlib import contextmanager


VERSIONS_FILE_URL='https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
BIN_DIR = os.path.expanduser('~/bin')
CHROMEDRIVERS_DIR = os.path.join(BIN_DIR, 'chromedrivers')
CHROMEDRIVER_LINK_PATH = os.path.join(BIN_DIR, 'chromedriver')

def download_json(json_url):
    response = requests.get(json_url)
    response.raise_for_status()
    return response.json()


def download_file(url, name = None, destdir = ''):
    name = name or os.path.basename(url)
    path = os.path.normpath(os.path.join(destdir, name))
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def download_versions_file():
    return download_json(VERSIONS_FILE_URL)

def ensure_dirs(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def extract_zip(filename, dest = None):
    with zipfile.ZipFile(filename, 'r') as zfile:
        zfile.extractall(dest)

def get_list_versions(limit = 0):
    versions_data = download_versions_file()
    versions = versions_data['versions']
    res = []
    for item in versions:
        res.append(item['version'])

    if limit > 0:
        res = res[-limit:-1]

    return res

def cmd_list_versions(limit = 0):
    versions = get_list_versions(limit=limit)
    for version in versions:
        print(version)
    print()


@contextmanager
def pushd(path):
    current_dir = os.getcwd()
    os.chdir(path)
    yield current_dir
    os.chdir(current_dir)


def configure():
    ensure_dirs(CHROMEDRIVERS_DIR)


def run(chromedriver_version):

    configure()

    chromedriver_versions = download_json(VERSIONS_FILE_URL)
    selected_version = None
    if chromedriver_version is None:
        # => Use latest
        selected_version = chromedriver_versions['versions'][-1]
    else:
        # => Use latest that matches:
        candidates = list(filter(lambda v: v['version'].startswith(chromedriver_version), chromedriver_versions['versions']))
        if len(candidates) > 0:
            selected_version = candidates[-1]

    if selected_version is None:
        print(f'Error: Chromedriver version not found: {chromedriver_version}')
        sys.exit()

    revision = selected_version['revision']
    platform = 'linux64'
    download_urls = selected_version['downloads']['chromedriver']
    linux_download_url_obj = list(filter(lambda x: x['platform'] == platform, download_urls))[0]
    linux_download_url = linux_download_url_obj['url']


    # Download zip:
    chromedriver_archive_name = f'chromedriver_{revision}.zip'
    download_file(linux_download_url, chromedriver_archive_name, CHROMEDRIVERS_DIR)

    with pushd(CHROMEDRIVERS_DIR):
        chromedriver_bin_name = f'chromedriver-{revision}'
        if not os.path.exists(chromedriver_bin_name):
            extract_zip(chromedriver_archive_name)

            shutil.copy('chromedriver-linux64/chromedriver', chromedriver_bin_name)
            os.chmod(chromedriver_bin_name, stat.S_IRWXU | stat.S_IRWXG)

        os.remove(CHROMEDRIVER_LINK_PATH)
        os.symlink(
            os.path.join(CHROMEDRIVERS_DIR, chromedriver_bin_name),
            CHROMEDRIVER_LINK_PATH
        )


if __name__ == '__main__':
    chromedriver_version = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--list':
            limit = 0
            if len(sys.argv) > 2:
                limit = int(sys.argv[2])
            cmd_list_versions(limit)
            sys.exit(0)

        chromedriver_version = sys.argv[1]

    run(chromedriver_version)

    #ensure_dirs(os.path.expanduser('~/bin/chromedrivers'))