import time

from flask import Flask, render_template, url_for
from flask_cors import CORS, cross_origin
from flask import request
from analyze_logs import parse_info_line
import json
import os
import shutil
import argparse
import logging
from multiprocessing import Process
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Erigon monitor params')
parser.add_argument('--no-dump-journal', dest="dumpjournal", action='store_false', help='No journal dump for debugging')
parser.add_argument('--host', dest="host", type=str, help='Host name', default="127.0.0.1")
parser.add_argument('--port', dest="port", type=int, help='Port number', default="5000")
parser.add_argument('--interval', dest="interval", type=int, help='Log scanning interval', default="30")
parser.add_argument('--erigon-data-path', dest="erigon_data_path", type=str, help='Path of erigon data', default=".")
parser.set_defaults(dumpjournal=True)

args = parser.parse_args()



total_events = 0

events_history = {}


# noinspection DuplicatedCode
def compute_events():
    if os.path.exists("erigon_current.log"):
        os.remove("erigon_current.log")
    if args.dumpjournal:
        os.system("/bin/bash dump_erigon_logs.sh")
    else:
        shutil.copy("erigon.log", "erigon_current.log")

    shutil.move("erigon_current.log", "current.log")

    loc_events = []
    for line in open("current.log"):
        info_split = line.split("[INFO]")

        if len(info_split) >= 2:
            line = "[INFO]" + "[INFO]".join(info_split[1:])
            if line.startswith("[INFO]"):
                try:
                    event = parse_info_line(line)
                    if event:
                        loc_events.append(event)
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
        size_history = {}

        if os.path.exists("size_history.json"):
            with open("size_history.json", "r") as r:
                size_history = json.loads(r.read())
        while True:
            try:
                erigon_data_folder = args.erigon_data_path

                total_size = 0
                for path, dirs, files in os.walk(erigon_data_folder):
                    for f in files:
                        fp = os.path.join(path, f)
                        total_size += os.path.getsize(fp)
                logger.info(f"Total size of directory {erigon_data_folder} {total_size})")
                size_history[datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")] = {
                    "erigon_data_size": total_size
                }
                with open("size_history_tmp.json", "w") as w:
                    w.write(json.dumps(size_history, indent=4, default=str))
                shutil.move("size_history_tmp.json", "size_history.json")

            except Exception as ex:
                logger.error(f"Failure when checking directory size: {ex}")


            #
            # This might take several minutes to complete
            try:
                loc_events = compute_events()

                events_history
                for ev in loc_events["events"]:
                    if ev["time"] not in events_history:
                        events_history[ev["time"]] = ev

                data = {}
                data["events"] = []
                for date_l in events_history:
                    data["events"].append(events_history[date_l])

                data["last_check"] = datetime.utcnow()

                with open("events_history_tmp.json", "w") as w:
                    w.write(json.dumps(data, indent=4, default=str))
                shutil.move("events_history_tmp.json", "events_history.json")
            except Exception as ex:
                logger.error(f"Problem encountered: {ex}")

            time.sleep(args.interval)



app = Flask(__name__)
cors = CORS(app)

response = {}


@app.route('/')
def hello():
    print("test")
    return 'Hello, World!'

@app.route('/html')
def html():
    return render_template('plot.html', events_url=url_for("events"), sizes_url=url_for("sizes"))

@app.route('/sizes')
@cross_origin()
def sizes():
    global events_history

    with open("size_history.json", "r") as f:
        resp = app.response_class(
            response=f.read(),
            status=200,
            mimetype='application/json'
        )
    return resp

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
    app.run(host=args.host, port=args.port, debug=True, use_reloader=False)
