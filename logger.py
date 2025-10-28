import csv
from datetime import datetime
import os

def log_metrics(step, queue_lengths, wait_time, filename="results.csv"):
    header = ["timestamp", "step", "lane1", "lane2", "lane3", "lane4", "wait_time"]
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        # write header only if file did not exist before
        if not file_exists:
            writer.writerow(header)
        writer.writerow([datetime.now(), step] + queue_lengths + [wait_time])
