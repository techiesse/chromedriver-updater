#!/usr/bin/env python3

import os
import platform
import shutil
import stat
import sys

import requests
import json
import zipfile

from contextlib import contextmanager, suppress


# FS utils:
def expanduser(*args, **kwargs):
    return os.path.normpath(os.path.expanduser(*args, **kwargs))

def path_join(*args, **kwargs):
    return os.path.normpath(os.path.join(*args, **kwargs))

#-------------------------------------------------------------------------------

VERSIONS_FILE_URL='https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
BIN_DIR = expanduser('~/bin')
CHROMEDRIVERS_DIR = path_join(BIN_DIR, 'chromedrivers')
CHROMEDRIVER_EXECUTABLE = {
    'Linux': 'chromedriver',
    'Windows': 'chromedriver.exe',
}


def get_chromedriver_link_path(system):
    return path_join(BIN_DIR, CHROMEDRIVER_EXECUTABLE[system])


def download_json(json_url):
    response = requests.get(json_url)
    response.raise_for_status()
    return response.json()


def download_file(url, name = None, destdir = ''):
    name = name or os.path.basename(url)
    path = os.path.normpath(path_join(destdir, name))
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def download_versions_file():
    return download_json(VERSIONS_FILE_URL)


def get_system_info():
    system_info = {
        'os': platform.system(),
        'bits': platform.architecture()[0],
    }
    return system_info


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

PLATFORMS = {
    '64bit': {
        'Linux': 'linux64',
        'Darwin': None,
        'Java': None,
        'Windows': 'win64',
    },
    '32bit': {
        'Linux': None,
        'Darwin': None,
        'Java': None,
        'Windows': 'win32',
    },
}


def run(chromedriver_version):
    system_info = get_system_info()

    configure()

    # Get chromedriver available versions:
    chromedriver_versions = download_json(VERSIONS_FILE_URL)

    # Select the desired chromedriver:
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
        sys.exit(1)

    revision = selected_version['revision']
    platform = PLATFORMS[system_info['bits']][system_info['os']]
    if platform is None:
        print(f'Platform not supported: {system_info["os"]} {system_info["bits"]}')
        sys.exit(2)
    download_urls = selected_version['downloads']['chromedriver']
    download_url_obj = list(filter(lambda x: x['platform'] == platform, download_urls))[0]
    download_url = download_url_obj['url']
    chromedriver_executable = CHROMEDRIVER_EXECUTABLE[system_info["os"]]

    # Download zip:
    chromedriver_archive_name = f'chromedriver_{revision}.zip'
    download_file(download_url, chromedriver_archive_name, CHROMEDRIVERS_DIR)

    # Extract and install:
    with pushd(CHROMEDRIVERS_DIR):
        chromedriver_bin_name = f'chromedriver-{revision}'
        if not os.path.exists(chromedriver_bin_name):
            extract_zip(chromedriver_archive_name)

            shutil.copy(
                os.path.normpath(f'chromedriver-{platform}/{chromedriver_executable}'),
                chromedriver_bin_name
            )
            os.chmod(chromedriver_bin_name, stat.S_IRWXU | stat.S_IRWXG)

        chromedriver_link_path = get_chromedriver_link_path(system_info['os'])
        with suppress(FileNotFoundError):
            os.remove(chromedriver_link_path)
        link_fn = shutil.copy if 'win' in platform else os.symlink
        link_fn(
            path_join(CHROMEDRIVERS_DIR, chromedriver_bin_name),
            chromedriver_link_path
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
