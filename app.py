from flask import Flask
from flask import request
from flask import render_template
import simplejson as json
from data_processing import *
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/crawl', methods=["POST"])
def crawl():
    try:
        body = request.json

        start = body["from"]
        end = body["to"]
    except Exception as e:
        print e
        errorMessage = "No field '%s' received\n\
        Request body should follow the pattern:\n\
         {'from':int, 'to':int}" % e.message
        return errorMessage, 400

    crawler = NpmCrawler()
    return str(crawler.startDependencyTimeMapping(start, end))


@app.route('/job/<jobId>')
def getJob(jobId):
    return json.dumps(NpmCrawler.getJob(jobId))


@app.route('/jobs')
def listJobs():
    return json.dumps(NpmCrawler.listJobs())


if __name__ == '__main__':
    app.run(debug=True)
