#!/usr/bin/env python2.7
import urllib2
import base64
import json
import os
import shutil

def googleSourcesGet(url):
    print "- Downloading " + url
    response = urllib2.urlopen(url)
    data = response.read()
    return base64.b64decode(data)

def mergeProtocols():
    print "- Merging JS and Browser protocol"
    browserProtoDomains = []
    jsProtoDomains = []

    with open("cache/browser_protocol.json") as f:
        browserProtoDomains = json.load(f)["domains"]

    with open("cache/js_protocol.json") as f:
        jsProtoDomains = json.load(f)["domains"]

    with open("cache/protocol.json", "w") as f:
        f.write(json.dumps({
            "version": { "major": "1", "minor": "2" },
            "domains": browserProtoDomains + jsProtoDomains
        }))

if not os.path.isfile("cache/js_protocol.json"):
    data = googleSourcesGet("https://chromium.googlesource.com/v8/v8/+/master/src/inspector/js_protocol.json?format=TEXT")
    with open("cache/js_protocol.json", "w") as f:
        f.write(data)

if not os.path.isfile("cache/browser_protocol.json"):
    data = googleSourcesGet("https://chromium.googlesource.com/chromium/src/+/56.0.2924.87/third_party/WebKit/Source/core/inspector/browser_protocol.json?format=TEXT")
    with open("cache/browser_protocol.json", "w") as f:
        f.write(data)

if not os.path.isfile("cache/CSSProperties.json5"):
    data = googleSourcesGet("https://chromium.googlesource.com/chromium/src/+/56.0.2924.87/third_party/WebKit/Source/core/inspector/browser_protocol.json?format=TEXT")
    with open("cache/CSSProperties.json5", "w") as f:
        f.write(data)

if not os.path.isfile("cache/protocol.json"):
    mergeProtocols()

if not os.path.isdir("devtools/"):
    os.mkdir("devtools/")

if not os.path.isfile("devtools/InspectorBackendCommands.js"):
    print("- Generating protocol files")
    os.system("python2.7 ../scripts/build/code_generator_frontend.py cache/protocol.json --output_js_dir devtools/")  

if not os.path.isfile("devtools/SupportedCSSProperties.js"):
    print("- Generating supported CSS properties JS file")
    os.system("python2.7 ../scripts/build/generate_supported_css.py cache/CSSProperties.json5 devtools/SupportedCSSProperties.js")

if not os.path.isdir("devtools/Images/"):
    print("- Copying devtools images")
    os.mkdir("devtools/Images/")
    shutil.copy2("../front_end/Images/toolbarButtonGlyphs.png", "devtools/Images/")

print("- Building chrome devtools")
os.system("python2.7 ../scripts/build/build_release_applications.py inspector --input_path ../front_end/ --output_path  devtools/")
