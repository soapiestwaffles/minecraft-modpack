#!/usr/bin/env python
# Quick and (so very very) dirty script to build modpack based on yamlvalues
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




# TODO D.R.Y.

import yaml
import pprint
import requests
import pathlib
import os
import shutil
import re
import json
import sys
from urllib.parse import urlparse
from uritemplate import URITemplate, expand

MODPACK_FILE = 'modpack.yml'
OUTDIR = os.path.join("out")

def parseModpackDefinitions(file):
    with open(file=file, mode="r") as file:
        modpack = yaml.load(file, Loader=yaml.FullLoader)

    return modpack


def main():
    print("Creating release...")

    # PARSE MODPACK YAML
    print("* Parsing modpack file")
    modpack = parseModpackDefinitions(MODPACK_FILE)

    headers = {
        'Authorization': 'token ' + os.environ['GITHUB_TOKEN'],
        'Content-type': 'application/json'
    }

    # POST /repos/:owner/:repo/releases
    print("* Creating release")

    with open('release.json', 'r') as f:
        releaseJson = f.read()

    # payload = {
    #     "tag_name": modpack['version'],
    #     "name": "Release {}".format(modpack['version']),
    #     "draft": False,
    #     "prerelease": False,
    #     "body": releaseJson
    # }
    createResult = requests.post('https://api.github.com/repos/soapiestwaffles/minecraft-modpack/releases', headers=headers, data=releaseJson)
    print("   === HTTP {}".format(createResult.status_code))
    if createResult.status_code != 201:
        print("!!! Error creating release")
        print(createResult.json())
        os._exit(1)

    createResult = createResult.json()

    print("* Uploading release asset")
    zipFilename = "soapiestwaffles-modpack.zip"
    template = URITemplate(createResult['upload_url'])
    uploadUrl = template.expand(name=zipFilename)
    headers = {
        'Authorization': 'token ' + os.environ['GITHUB_TOKEN'],
        'Content-type': 'application/octet-stream',
        'Accept': 'application/json'
    }
    with open(os.path.join(OUTDIR, zipFilename), 'rb') as f:
        assetResult = requests.post(uploadUrl, data=f, headers=headers)
    print("   === HTTP {}".format(assetResult.status_code))
    if assetResult.status_code != 201:
        print("!!! Error uploading release asset")
        print(assetResult.json())
        os._exit(1)


if __name__ == "__main__":
    print("Running create-release")
    main()