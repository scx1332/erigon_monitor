from datetime import datetime
import json

def get_date_from_line(line):
    splits = line.split("[")
    date_part = splits[2].split("]")[0]
    date_day_month = date_part.split("|")[0]
    date_time = date_part.split("|")[1]

    current_year = datetime.now().year
    month = int(date_day_month.split("-")[0])
    day = int(date_day_month.split("-")[1])
    hour = int(date_time.split(":")[0])
    minute = int(date_time.split(":")[1])
    seconds = int(date_time.split(":")[2].split(".")[0])
    millis = int(date_time.split(":")[2].split(".")[1])

    dt = datetime(current_year, month, day, hour, minute, seconds, millis * 1000)
    return dt


def parse_snapshot_line(line):
    print(line)
    after_progress = line.split('progress="')[1]
    percent = float(after_progress.split("%")[0])
    print(percent)

    return {
        "progress": percent
    }
    #raise Exception("stop")

def parse_headers_line(line):
    return {
        "progress": "todo"
    }

def parse_bodies_line(line):
    return {
        "progress": "todo"
    }

def parse_execution_line(line):
    return {
        "progress": "todo"
    }


def parse_info_line(line):
    dt = get_date_from_line(line)
    event = {
        "time": dt
    }
    if "[Snapshots] download" in line:
        event["type"] = "snapshot"
        event["info"] = parse_snapshot_line(line)
        print("Downloading snapshots")

    if "[1/16 Headers]" in line:
        event["type"] = "headers"
        event["info"] = parse_headers_line(line)

    if "[4/16 Bodies]" in line:
        event["type"] = "bodies"
        event["info"] = parse_bodies_line(line)

    if "[6/16 Execution]" in line:
        event["type"] = "execution"
        event["info"] = parse_execution_line(line)

    return event

    #print(f"Datetime parsed {dt} from {line}")


events = []
for line in open("goerli_err.log"):
    if line.startswith("[INFO]"):
        try:
            events.append(parse_info_line(line))
        except Exception as ex:
            print(f"Error when parsing {ex}")
    else:
        print("Unknown line")

with open("output.json", "w") as f:
    f.write(json.dumps(events, indent=4, default=str))
print(json.dumps(events, indent=4, default=str))
