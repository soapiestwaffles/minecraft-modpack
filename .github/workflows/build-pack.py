#!/usr/bin/env python

# Quick and (very very) dirty script to build modpack based on yamlvalues
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

# TODO add optifine downloader

import yaml
from jinja2 import Template
import pprint
import requests
import pathlib
import os
import shutil
import re
import json
from urllib.parse import urlparse

MODPACK_FILE = 'modpack.yml'
OUTDIR = os.path.join("out", "soapiestwaffles-modpack")

RELEASE_TEMPLATE = """
**Forge version:** {{ modpack.forge.version }}

Included mods:
{% for mod in modpack.mods %}
* {{ mod.name }}
  * version: {{ mod.version }}
  * url: {{ mod.modUrl }}
{% endfor %}
"""

def parseModpackDefinitions(file):
    with open(file=file, mode="r") as file:
        modpack = yaml.load(file, Loader=yaml.FullLoader)

    return modpack

def generateReleaseDoc(modpack, template):
    template = Template(template)
    return template.render(modpack=modpack)

def createModPackDir(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

def getFilenameFromUrl(url):
    parsed = urlparse(url)
    return os.path.basename(parsed.path)

# {"tag_name": "v1.0.0","target_commitish": "master","name": "v1.0.0","body": "Release of version 1.0.0","draft": false,"prerelease": false}
def createReleaseJson(modpack, releasetxt):
    release = {
        "body": releasetxt,
        "draft": False,
        "prerelease": False,
        "name": "Release {}".format(modpack['version']),
        "tag_name": modpack['version']
    }

    return json.dumps(release)


def downloadFile(destination, url):
    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

    headers = {
        'User-Agent': userAgent
    }
    s = requests.Session()
    with s.get(url, headers=headers, stream=True) as r:
        print("    === HTTP {}".format(r.status_code))
        if r.status_code == 200:
            with open(os.path.join(destination, getFilenameFromUrl(url)), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)


def main():
    # PARSE MODPACK YAML
    print("* Parsing modpack file")
    modpack = parseModpackDefinitions(MODPACK_FILE)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(modpack)

    # OUTPUT DIR
    print("* Creating pack output directory")
    createModPackDir(os.path.join(OUTDIR, "mods"))

    # DOWNLOAD FORGE
    print("* Downloading Forge")
    downloadFile(OUTDIR, modpack['forge']['url'])

    # DOWNLOAD MODS
    print("* Downloading mods")
    for mod in modpack['mods']:
        print("  > Downloading mod: {} ({})".format(mod['name'], mod['downloadUrl']))
        downloadFile(os.path.join(OUTDIR, "mods"), mod['downloadUrl'])


    # GENERATE RELEASE DOCUMENTATION
    print("* Generating release document")
    releaseDoc = generateReleaseDoc(modpack, RELEASE_TEMPLATE)
    with open(os.path.join(OUTDIR, "RELEASE.md"), 'w') as f:
        f.write(releaseDoc)
    print("===")
    print(releaseDoc)
    print("===")

    # GENERATE RELEASE JSON
    print("* Generating release JSON")
    with open("release.json", 'w') as f:
        f.write(createReleaseJson(modpack, releaseDoc))


if __name__ == "__main__":
    main()



