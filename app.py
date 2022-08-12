from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from analyze_logs import parse_info_line
import json
import os
import shutil
import argparse
from multiprocessing import Process



parser = argparse.ArgumentParser(description='Erigon monitor params')
parser.add_argument('--no-dump-journal', dest="dumpjournal", action='store_false', help='No journal dump for debugging')
parser.add_argument('--host', dest="host", type=str, help='Host name', default="127.0.0.1")
parser.add_argument('--port', dest="port", type=int, help='Port number', default="5000")
parser.set_defaults(dumpjournal=True)

args = parser.parse_args()



total_events = 0

events_history = {}


# noinspection DuplicatedCode
def compute_events():
    if os.path.exists("current.log"):
        os.remove("current.log")
    if args.dumpjournal:
        os.system("/bin/bash dump_erigon_logs.sh")
    else:
        shutil.copy("erigon.log", "current.log")

    loc_events = []
    for line in open("current.log"):
        info_split = line.split("[INFO]")

        if len(info_split) >= 2:
            line = "[INFO]" + "[INFO]".join(info_split[1:])
            if line.startswith("[INFO]"):
                try:
                    loc_events.append(parse_info_line(line))
                except Exception as ex:
                    print(f"Error when parsing {ex}")
            else:
                print("Unknown line")

    return {"events": loc_events}


class ProcessClass:
    def __init__(self):
        # = Process(target=self.run, args=())
        # p.daemon = True                       # Daemonize it
        # p.start()                             # Start the execution
        pass

    def run(self):

        #
        # This might take several minutes to complete
        loc_events = compute_events()

        global events_history
        for ev in loc_events["events"]:
            if ev["time"] not in events_history:
                events_history[ev["time"]] = ev

        print(len(events_history))


app = Flask(__name__)
cors = CORS(app)

response = {}


@app.route('/')
def hello():
    print("test")
    return 'Hello, World!'


@app.route('/start')
def start():
    begin = ProcessClass()
    begin.run()

    return "Task is in progress"


@app.route('/events')
@cross_origin()
def events():
    global events_history
    data = {}
    data["events"] = []
    for date in events_history:
        data["events"].append(events_history[date])

    resp = app.response_class(
        response=json.dumps(data, indent=4, default=str),
        status=200,
        mimetype='application/json'
    )
    return resp

if __name__ == "__main__":
    print("test")
    app.run(host=args.host, port=args.port, debug=True)
