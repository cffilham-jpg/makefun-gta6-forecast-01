"""Offline launch-day quantiles learned from the supplied launch histories."""

import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path


# Use the middle of the broad practice plateau, rather than its fitted minimum.
SHRINK = 0.55
NORMAL_SCORES = (-1.645, -0.674, 0.0, 0.674, 1.645)


def percentile(ordered, fraction):
    position = fraction * (len(ordered) - 1)
    left = int(position)
    right = min(left + 1, len(ordered) - 1)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


def instant(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def anchor(case):
    for observation in case.get("known", []):
        if observation.get("hour") == 1:
            value = float(observation["viewers"])
            if math.isfinite(value):
                return min(1e9, max(1.0, value))
    return 1.0


def persistence(value):
    return {"hours": [{"hour": hour, "q": [value] * 5}
                      for hour in range(2, 25)]}


def estimate(case, value):
    changes = [[] for _ in range(23)]
    for launch in case.get("comparables", []):
        try:
            start = instant(launch["day_start"])
            series = {instant(point["from"]): point["viewers"]
                      for point in launch["hourly"]}
            counts = [float(series[start + timedelta(hours=offset)])
                      for offset in range(24)]
            if counts[0] < 100 or any(not math.isfinite(x) or x < 0 for x in counts):
                continue
            for index, count in enumerate(counts[1:]):
                changes[index].append(math.log(max(1.0, count) / counts[0]))
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
    if not changes[0]:
        return persistence(value)
    rows = []
    for hour, sample in enumerate(changes, 2):
        sample.sort()
        center = percentile(sample, 0.5)
        sigma = max(0.12, (percentile(sample, 0.75) - percentile(sample, 0.25)) / 1.349)
        log_values = [math.log(value) + center + z * sigma * SHRINK
                      for z in NORMAL_SCORES]
        quantiles = [min(1e9, math.exp(min(math.log(1e9), max(-20.0, x))))
                     for x in log_values]
        rows.append({"hour": hour, "q": quantiles})
    return {"hours": rows}


def run():
    destination = Path(os.getenv("MAKEFUN_OUTPUT_DIR", "/output"))
    destination.mkdir(parents=True, exist_ok=True)
    source = Path(os.getenv("MAKEFUN_INPUT_DIR", "/input"))
    for item in sorted(source.glob("*.in")):
        value = 1.0
        try:
            case = json.loads(item.read_bytes())
            value = anchor(case)
            result = estimate(case, value)
        except Exception:
            result = persistence(value)
        encoded = json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n"
        destination.joinpath(item.stem + ".out").write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    run()
