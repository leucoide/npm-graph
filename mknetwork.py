import simplejson as json
from graph_tool.all import *
from unqlite import UnQLite
import matplotlib.pyplot as plt

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

    # def consolidateDaysUntil(timeIndex):
    #     previousDays = []
    #     for ti in range(1, timeIndex+1):
    #         m = self.mergeUntil(ti)
    #         if previousDays != []:
    #             if m f g:
    #                 pass

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


class Day(object):
    """docstring for Day"""
    def __init__(self, timeIndex):
        super(Day, self).__init__()
        self.timeIndex = timeIndex


# tm = json.load(open("datasets/dependencies_times_0_to_100.json", "r"))
# ts = TimedSet(tm)
# ts.consolidateToDB()
# g = DBTimedSet().networkOn(150)

# g = ts.networkOn(100)
# notAlone = g.new_vertex_property("bool")
# for v in g.vertices():
#     notAlone[v] = (v.out_degree() > 0) or (v.in_degree() > 0)
# # g.set_vertex_filter(notAlone)
#
# # graph_draw(g, output="datasets/_10th.png")
# rootVertex = g.vertex(0)
# for v in g.vertices():
#     if v.in_degree() > rootVertex.in_degree():
#         rootVertex = v
# pos = arf_layout(g, a=3.5, d=.5, max_iter=1e4)
# # pos = fruchterman_reingold_layout(g)
# graph_draw(g, pos=pos, vertex_size=10)
