import time

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
        p = Process(target=self.run, args=())
        p.daemon = True                       # Daemonize it
        p.start()                             # Start the execution
        pass

    def run(self):

        while True:
            #
            # This might take several minutes to complete
            loc_events = compute_events()

            events_history
            for ev in loc_events["events"]:
                if ev["time"] not in events_history:
                    events_history[ev["time"]] = ev

            data = {}
            data["events"] = []
            for date in events_history:
                data["events"].append(events_history[date])

            with open("events_history.json", "w") as w:
                w.write(json.dumps(data, indent=4, default=str))

            time.sleep(10.0)



app = Flask(__name__)
cors = CORS(app)

response = {}


@app.route('/')
def hello():
    print("test")
    return 'Hello, World!'




@app.route('/events')
@cross_origin()
def events():
    global events_history

    with open("events_history.json", "r") as f:
        resp = app.response_class(
            response=f.read(),
            status=200,
            mimetype='application/json'
        )
    return resp

if __name__ == "__main__":
    print("test")
    begin = ProcessClass()
    app.run(host=args.host, port=args.port, debug=True)
