# makefun-gta6-forecast-01

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cffilham-jpg/makefun-gta6-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cffilham-jpg/makefun-gta6-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

An offline, deterministic v3 forecast of GTA VI's launch-day Twitch viewers for hours 2–24 UTC. Complete comparable launch days supply hourly log-ratios relative to hour 1. A Gaussian kernel weights comparables by how closely their pre-release 24-hour peak relative to hour 1 matches the case's own signal. The bandwidth starts at 0.5 and widens while the effective sample size is below six, up to the specified 0.8 stopping threshold.

Interpolated weighted percentiles supply the center and an IQR-based log spread, floored at 0.12 and multiplied by 0.55. The center percentile starts at the 70th and adapts to the case's hour-1 audience concentration: it shifts up when the target's viewers-per-channel is below the comparables' median (a broad audience, which grows more through the day) and down when above (a concentrated audience), clipped to the [0.45, 0.72] range. Missing comparable pre-signals use the available signals' median. Without a usable case or comparable pre-signal, the forecast uses uniform weights and a median center; without complete comparables, it uses persistence. Profiles are learned at runtime, with no filtering by unlock notes, game, platform, or date.

Python standard library only. Unexpected per-case errors fall back to hour-1 persistence. No practice answers or fitted hourly profiles are shipped.

Local practice validation: mean pinball loss **0.153596** (v2: 0.186060, v1: 0.268294), typical miss **25.25%**, and 90% coverage **0.880**. Leave-one-launch-out (each practice case scored with the other three practice launches added as comparables): **0.154711** (v2: 0.202717). These practice results do not guarantee final performance.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The sandbox defaults are `/input` and `/output`. Every input `.in` file produces a matching `.out` file containing five ordered quantiles for each of the 23 forecast hours.

<sub>Entered on [make.fun](https://make.fun/?ref=tv86zvxh&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
