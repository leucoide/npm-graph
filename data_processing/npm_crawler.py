import requests
import threading
import time
import simplejson as json
from timed_set import *


NPM_URL = "http://registry.npmjs.com"


class NpmCrawler(object):
    """docstring for NpmCrawler"""
    def __init__(self):
        super(NpmCrawler, self).__init__()

    def startDependencyTimeMapping(self, start=None, end=100):
        jobId = NpmCrawler.addJob()
        thread = threading.Thread(target=self.mkDependencyTimeMapping,
                                  args=(jobId, start, end))
        thread.start()
        return jobId

    def mkDependencyTimeMapping(self, jobId, start=None, end=100):
        start = start - 1 if start is not None else 0
        time_map = json.load(open("datasets/last_times.json", "r"))
        dates = sorted(time_map.keys())[start:end]
        total = reduce(lambda x, y: x+y,
                       [len(time_map[i]) for i in dates])
        failedPackages = {}
        newMap = {}
        jobStatus = {"total": total, "current": 0,
                     "meanStepTime": 0, "timeOfStep": time.time(),
                     "startPoint": start+1, "endPoint": end}
        NpmCrawler.updateJob(jobId, jobStatus)
        # print NpmCrawler.getJob(jobId)
        # print NpmCrawler._jobs[jobId]
        for date in dates:
            newMap[date] = []
            failedPackages[date] = []
            for pkg in time_map[date]:
                try:
                    dependencies = self.getPkg(pkg["package"],
                                               pkg["version"])["dependencies"]
                    dependencies = [{"package": key,
                                    "version": dependencies[key]}
                                    for key in dependencies.keys()]
                except KeyError as e:
                    dependencies = []
                except requests.exceptions.ConnectionError as error:
                    failedPackages[date] += [pkg]
                    dependencies = []
                status = NpmCrawler.getJob(jobId)
                timeOfStep = time.time()
                timeElapsed = timeOfStep - status["timeOfStep"]
                meanStepTime = (status["meanStepTime"]*status["current"] +
                                timeElapsed)
                meanStepTime /= (status["current"] + 1)
                status["current"] += 1
                status["timeOfStep"] = timeOfStep
                status["meanStepTime"] = meanStepTime
                NpmCrawler.updateJob(jobId, status)
                pkg["dependencies"] = dependencies
                newMap[date] += [pkg]

        TimedSet(newMap).consolidateToOrchestrate()
        self.writeToFile({
            "path": "datasets/FAIL_dependencies_times_%s_to_%s.json"
                    % (start+1, end),
            "content": json.dumps(failedPackages)
            })

    def writeToFile(self, *itens):
        for item in itens:
            out = open(item["path"], "w+")
            out.write(item["content"])
            out.close()

    def getPkg(self, name, version=None):
        url = "%s/%s" % (NPM_URL, name)
        url = url if version is None else "%s/%s" % (url, version)
        return requests.get(url).json()

    @staticmethod
    def addJob():
        jobId = len(NpmCrawler._jobs.keys())+1
        NpmCrawler._jobs[jobId] = {}
        return jobId

    @staticmethod
    def updateJob(jobId, obj):
        NpmCrawler._jobs[jobId] = obj
        # print NpmCrawler.getJob(jobId)
        return jobId

    @staticmethod
    def getJob(jobId):
        return NpmCrawler._jobs[int(jobId)]

    @staticmethod
    def listJobs():
        return NpmCrawler._jobs.keys()


NpmCrawler._jobs = {}
