import json
import csv
import sys


def create_entry(name, value, unit):
    entry = {
        "name": name,
        "value": value,
        "unit": unit
    }
    return entry


def read_metric(metric):
    task = metric.get("task")
    throughput = metric.get("throughput")
    latency = metric.get("latency")
    service_time = metric.get("service_time")
    client_processing_time = metric.get("client_processing_time")
    processing_time = metric.get("processing_time")
    error_rate = metric.get("error_rate")
    return [
        create_entry(f"{task} throughput mean", 1 % throughput.get("mean"), "s/ops"),
        create_entry(f"{task} latency mean", latency.get("mean"), "ms"),
        create_entry(f"{task} error rate", error_rate * 100, "%")
    ]


def rewrite_results(src_file):
    try:
        result = []
        with open(src_file, 'r') as f:
            src = json.load(f)
        results = src.get("results")
        metrics = results.get("op_metrics")
        for metric in metrics:
            result.extend(read_metric(metric))
        return result
    except Exception as e:
        print(f"Failed to rewrite benchmark results: {e}")
        sys.exit(1)


def rewrite_csv(src_file):
    try:
        result = []
        with open(src_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row[1] == "" or row[1] is None:
                    continue
                else:
                    name = f"{row[0]} {row[1]}"
                if name.startswith("Min") or name.startswith("Max") or name.startswith("Median"):
                    continue
                unit = row[3]
                value = float(row[2])
                if unit == "ops/s":
                    value = 1 / value
                    unit = "s/ops"
                entry = create_entry(name, value, unit)
                result.append(entry)
            return result
    except Exception as e:
        print(f"Failed to rewrite benchmark results: {e} {row}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Wrong number of arguments")
        sys.exit(1)
    else:
        src = sys.argv[1]
        dest = sys.argv[2]
        json_res = rewrite_csv(src)
        with open(dest, 'w') as f:
            json.dump(json_res, f, indent=4)
