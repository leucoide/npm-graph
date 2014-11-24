# -*- coding: utf-8 -*-
# from graph_tool.all import *
import requests
from progressbar import *
import json
import re
from mknetwork import *

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


def mk_dependency_time_mapping(start=None, end=100):
    start = start - 1 if start is not None else 0
    time_map = json.load(open("datasets/last_times.json", "r"))
    dates = sorted(time_map.keys())[start:end-1]
    total = reduce(lambda x, y: x+y,
                   [len(time_map[i]) for i in dates])
    failedPackages = {}
    newMap = {}
    pb = ProgressBar(total)
    for date in dates:
        newMap[date] = []
        failedPackages[date] = []
        for pkg in time_map[date]:
            try:
                dependencies = get_pkg(pkg["package"],
                                       pkg["version"])["dependencies"]
                dependencies = [{"package": key, "version": dependencies[key]}
                                for key in dependencies.keys()]
                # print dependencies
            except KeyError as e:
                dependencies = []
            except requests.exceptions.ConnectionError as error:
                failedPackages[date] += [pkg]
                dependencies = []

            pkg["dependencies"] = dependencies
            newMap[date] += [pkg]
            pb.tick()

    TimedSet(newMap).consolidateToDB()
    writeToFile({
        "path": "datasets/FAIL_dependencies_times_%s_to_%s.json"
                % (start+1, end),
        "content": json.dumps(failedPackages)
        })
    # writeToFile({
    #     "path": "datasets/dependencies_times_%s_to_%s.json" % (start+1, end),
    #     "content": json.dumps(newMap)},
    #     {
    #     "path": "datasets/FAIL_dependencies_times_%s_to_%s.json"
    #             % (start+1, end),
    #     "content": json.dumps(failedPackages)
    #     })

    # out = open("datasets/dependencies_times_0_to_%s.json" % end, "w+")
    # out.write(json.dumps(newMap))
    # out.close()
    #
    # fail = open("datasets/FAIL_dependencies_times_0_to_%s.json" % end, "w+")
    # fail.write(json.dumps(failedPackages))
    # fail.close()


def writeToFile(*itens):
    for item in itens:
        out = open(item["path"], "w+")
        out.write(item["content"])
        out.close()

mk_dependency_time_mapping(101, 200)
