# -*- coding: utf-8 -*-
# from graph_tool.all import *
import requests
from progressbar import *
import json
import re

NPM_URL = "http://registry.npmjs.com"


def get_all_pkgs():
    # url = "%s/-/all" % NPM_URL
    # return requests.get().json
    return json.load(open("datasets/all.json"))


def get_pkg(name, version=None):
    url = "%s/%s" % (NPM_URL, name)
    url = url if version is None else "%s/%s" % (url, version)
    return requests.get(url).json()


def mk_time_version_mapping():
    all_pkgs = get_all_pkgs()
    pb = ProgressBar(len(all_pkgs.keys()))
    json_out = {}
    for pkg in all_pkgs.keys():
        pb.tick()
        try:
            times = get_pkg(pkg)["time"]
            for version in times.keys():
                day = re.search("\w+-\w+-\w+(?=T)", times[version]).group(0)
                try:
                    json_out[day]
                except KeyError as e:
                    json_out[day] = []

                json_out[day] += [{pkg: version}]
        except Exception as e:
            pass
    out = open("datasets/times.json", "w+")
    out.write(json.dumps(json_out))
    out.close()


def mk_dependency_time_mapping():
    time_map = json.load(open("datasets/last_times.json", "r"))
    total = reduce(lambda x, y: x+y,
                   [len(time_map[i]) for i in time_map.keys()])
    pb = ProgressBar(total)
    for date in time_map.keys():
        for pkg in time_map[date]:
            try:
                dependencies = get_pkg(pkg["pakage"],
                                       pkg["version"])["dependencies"]
                dependencies = [{"pakage": key, "version": dependencies[key]}
                                for key in dependencies.keys()]
                # print dependencies
            except KeyError as e:

                dependencies = []

            pkg["dependencies"] = dependencies
            pb.tick()

    out = open("datasets/dependencies_times.json", "w+")
    out.write(json.dumps(time_map))
    out.close()

mk_dependency_time_mapping()
