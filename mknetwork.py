import json
from graph_tool.all import *


class TimedSet(object):
    """docstring for TimedSet"""
    def __init__(self, timeMap):
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

    def networkOn(self, timeIndex):
        v_map = {}
        g = Graph()
        m = self.mergeUntil(timeIndex)
        for pkg in m:
            v_map[pkg["package"]] = g.add_vertex()

        for pkg in m:
            for d in pkg["dependencies"]:
                try:
                    v_map[d["package"]]
                except KeyError as e:
                    v_map[d["package"]] = g.add_vertex()

                v1 = v_map[pkg["package"]]
                v2 = v_map[d["package"]]
                g.add_edge(v1, v2)
        return g


tm = json.load(open("datasets/dependencies_times_0_to_100.json", "r"))
ts = TimedSet(tm)
g = ts.networkOn(100)
notAlone = g.new_vertex_property("bool")
for v in g.vertices():
    notAlone[v] = (v.out_degree() > 0) or (v.in_degree() > 0)
# g.set_vertex_filter(notAlone)

# graph_draw(g, output="datasets/_10th.png")
rootVertex = g.vertex(0)
for v in g.vertices():
    if v.in_degree() > rootVertex.in_degree():
        rootVertex = v
pos = arf_layout(g, a=3.5, d=.5, max_iter=1e4)
# pos = fruchterman_reingold_layout(g)
graph_draw(g, pos=pos, vertex_size=10)
