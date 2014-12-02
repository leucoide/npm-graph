import simplejson as json
from graph_tool.all import *
from unqlite import UnQLite
import config
from porc import Client

DB_PATH = "datasets/data.db"


class TimedSet(object):
    """docstring for TimedSet"""
    def __init__(self, timeMap=None):
        super(TimedSet, self).__init__()
        self.timeMap = timeMap
        self.times = sorted(timeMap.keys())

    def mergeUntil(self, timeIndex):
        times = self.times[:timeIndex]
        mergedSet = []
        readPackages = []
        for t in times[::-1]:
            for pkg in self.timeMap[t]:
                if pkg["package"] not in readPackages:
                    mergedSet += [pkg]
                    readPackages += [pkg["package"]]
        return mergedSet

    def consolidateToDB(self):
        db = UnQLite(DB_PATH)
        times = db.collection("times")
        if not times.exists():
            times.create()
        for t in self.timeMap.keys():
                times.store({t: self.timeMap[t]})
        db.commit()
        db.close()

    def consolidateToOrchestrate(self):
        client = CLient(config.PORC_KEY)
        for time in self.times:
            date_list = [int(i) for i in time.split("-")]
            date = datetime(date_list[0], date_list[1], date_list[2])
            resp = client.post_event(col_name,
                                     "daily_entry",
                                     "daily_entry",
                                     {"entries": self.timeMap[time]},
                                     date)
            resp.raise_for_status()

    def networkOn(self, timeIndex):
        v_map = {}
        g = Graph()
        packageName = g.new_vertex_property("string")
        g.vertex_properties["name"] = packageName
        m = self.mergeUntil(timeIndex)
        for pkg in m:
            v_map[pkg["package"]] = g.add_vertex()
            packageName[v_map[pkg["package"]]] = pkg["package"]

        for pkg in m:
            for d in pkg["dependencies"]:
                try:
                    v_map[d["package"]]
                except KeyError as e:
                    v_map[d["package"]] = g.add_vertex()
                    packageName[v_map[d["package"]]] = d["package"]

                v1 = v_map[pkg["package"]]
                v2 = v_map[d["package"]]
                g.add_edge(v1, v2)
        return g


class DBTimedSet(TimedSet):
    """docstring for DBTimedSet"""
    def __init__(self, dbPath=DB_PATH):
        self.timeMap = self.getTimesFromDB(dbPath).convertFromDBToTimeMap()
        super(DBTimedSet, self).__init__(self.timeMap)

    def getTimesFromDB(self, dbPath):
        db = UnQLite(DB_PATH)
        times = db.collection("times")
        if not times.exists():
            raise Exception("No data to retrieve")
        self.dbData = times.all()
        return self

    def convertFromDBToTimeMap(self):
        tm = {}
        for data in self.dbData:
            for d in data.keys():
                if d != "__id":
                    tm[d] = data[d]
        return tm
