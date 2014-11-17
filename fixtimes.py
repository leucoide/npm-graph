import json


def times_to_formated_objects():
    d = json.load(open("datasets/times.json", "r"))

    newd = {}

    for date in d.keys():
        for entry in d[date]:
            pkg = entry.keys()[0]
            if entry[pkg] != "created" and entry[pkg] != "modified":
                new_entry = {"pakage": pkg, "version": entry[pkg]}
                try:
                    newd[date]
                except KeyError as e:
                    newd[date] = []
                newd[date] += [new_entry]

    f = open("datasets/fixed_times.json", "w+")
    f.write(json.dumps(newd))
    f.close()


def formated_objects_to_simple_pkg_lists():
    d = json.load(open("datasets/fixed_times.json", "r"))
    newd = {}

    for date in d.keys():
        newd[date] = []
        for entry in d[date]:
            alreadyThere = False
            for p in newd[date]:
                if p == entry["pakage"]:
                    alreadyThere = True
                    break
            if not alreadyThere:
                try:
                    newd[date] += [entry["pakage"]]
                except KeyError as e:
                    print entry

    f = open("datasets/simple_times.json", "w+")
    f.write(json.dumps(newd))
    f.close()


def formated_objects_to_last_formated():
    d = json.load(open("datasets/fixed_times.json", "r"))
    newd = {}

    for date in d.keys():
        newd[date] = []
        for entry in d[date]:
            isLast = True
            for old_entry in newd[date]:
                if old_entry["pakage"] == entry["pakage"]:
                    # greater is last
                    if old_entry["version"] < entry["version"]:
                        newd[date].remove(old_entry)
                        isLast = True
                        break
                    else:
                        isLast = False
            if isLast:
                newd[date] += [entry]
    f = open("datasets/last_times.json", "w+")
    f.write(json.dumps(newd))
    f.close()

formated_objects_to_last_formated()
