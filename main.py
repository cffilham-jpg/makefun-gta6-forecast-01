"""Offline launch-day quantiles learned from the supplied launch histories."""

import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median


# Robust comparable spreads retain the v1 uncertainty shrinkage.
SHRINK = 0.55
NORMAL_SCORES = (-1.645, -0.674, 0.0, 0.674, 1.645)


def weighted_percentile(pairs, fraction):
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    if total <= 0:
        return pairs[len(pairs) // 2][0]
    target = fraction * total
    acc = 0.0
    prev_v = pairs[0][0]
    for v, w in pairs:
        if acc + w >= target:
            if w <= 0:
                return v
            if acc <= 0:
                return v
            return prev_v + (v - prev_v) * ((target - acc) / w)
        acc += w
        prev_v = v
    return pairs[-1][0]


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


def pre_signal(points, timestamp_key, start, first):
    lower = start - timedelta(hours=24)
    peak = None
    for point in points:
        when = instant(point[timestamp_key])
        if lower <= when < start:
            count = float(point["viewers"])
            if math.isfinite(count):
                peak = count if peak is None else max(peak, count)
    if peak is None or peak < 1:
        return None
    return math.log(max(1.0, peak) / first)


def estimate(case, value):
    profiles = []
    signals = []
    for launch in case.get("comparables", []):
        try:
            start = instant(launch["day_start"])
            series = {instant(point["from"]): point["viewers"]
                      for point in launch["hourly"]}
            counts = [float(series[start + timedelta(hours=offset)])
                      for offset in range(24)]
            if counts[0] < 100 or any(not math.isfinite(x) or x < 0 for x in counts):
                continue
            signal = pre_signal(launch["hourly"], "from", start, counts[0])
            profiles.append([math.log(max(1.0, count) / counts[0])
                             for count in counts[1:]])
            signals.append(signal)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
    if not profiles:
        return persistence(value)
    hourly = "history_hourly" in case
    first = next(float(row["viewers"]) for row in case["known"]
                 if row.get("hour") == 1)
    signal = pre_signal(case.get("history_hourly" if hourly else "history", []) or [],
                        "from" if hourly else "at", instant(case["day_start"]), first)
    available = [s for s in signals if s is not None]
    weights = [1.0] * len(profiles)
    center_fraction = 0.5
    if signal is not None and available:
        replacement = median(available)
        features = [replacement if s is None else s for s in signals]
        bandwidth = 0.2
        while True:
            weights = [math.exp(-((s - signal) / bandwidth) ** 2)
                       for s in features]
            squares = sum(w * w for w in weights)
            ess = sum(weights) ** 2 / squares if squares > 0 else 0.0
            if ess >= 6 or bandwidth >= 0.8:
                break
            bandwidth *= 1.25
        center_fraction = 0.65
    rows = []
    for index, hour in enumerate(range(2, 25)):
        sample = [(profile[index], weight)
                  for profile, weight in zip(profiles, weights)]
        center = weighted_percentile(sample, center_fraction)
        sigma = max(0.12, (weighted_percentile(sample, 0.75)
                           - weighted_percentile(sample, 0.25)) / 1.349)
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
