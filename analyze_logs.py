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

def parse_execution_limits_line(line):
    info = {}
    info["from"] = line.split("from=")[1].split(" ")[0]
    info["to"] = line.split("to=")[1].split(" ")[0]
    return info

def parse_execution_line(line):
    info = {}
    info["blk_num"] = line.split("number=")[1].split(" ")[0]
    info["blk_per_s"] = line.split("blk/s=")[1].split(" ")[0]
    info["tx_per_s"] = line.split("tx/s=")[1].split(" ")[0]
    info["mgas_per_s"] = line.split("Mgas/s=")[1].split(" ")[0]
    info["gas_state"] = line.split("gasState=")[1].split(" ")[0]
    info["batch_size"] = line.split("batch=")[1].split(" ")[0]
    info["alloc"] = line.split("alloc=")[1].split(" ")[0]
    info["sys"] = line.split("sys=")[1].split("\n")[0]
    return info




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
        if "Executed blocks" in line:
            event["type"] = "execution"
            event["info"] = parse_execution_line(line)
        if "Blocks execution" in line:
            event["type"] = "execution_limits"
            event["info"] = parse_execution_limits_line(line)


    return event

    #print(f"Datetime parsed {dt} from {line}")

if __name__ == "__main__":
    events = []
    for line in open("erigon.log"):
        info_split = line.split("[INFO]")

        if len(info_split) >= 2:
            line = "[INFO]" + "[INFO]".join(info_split[1:])
            if line.startswith("[INFO]"):
                try:
                    events.append(parse_info_line(line))
                except Exception as ex:
                    print(f"Error when parsing {ex}")
            else:
                print("Unknown line")

    response = {}
    response["events"] = events

    with open("output.json", "w") as f:
        f.write(json.dumps(response, indent=4, default=str))
    print(json.dumps(response, indent=4, default=str))

