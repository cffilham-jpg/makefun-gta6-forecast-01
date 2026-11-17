# makefun-gta6-forecast-01

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cffilham-jpg/makefun-gta6-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cffilham-jpg/makefun-gta6-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

An offline, deterministic forecast of GTA VI's launch-day Twitch viewers for hours 2–24 UTC. Each input's complete comparable launch days supply hourly log-ratios relative to hour 1. Their median supplies the forecast center; their IQR supplies a robust log spread, floored at 0.12 and multiplied by 0.55. Profiles are learned at runtime, with no filtering by unlock notes, game, platform, or date.

Python standard library only. Unexpected per-case errors fall back to hour-1 persistence. No practice answers or fitted hourly profiles are shipped.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The sandbox defaults are `/input` and `/output`. Every input `.in` file produces a matching `.out` file containing five ordered quantiles for each of the 23 forecast hours.

<sub>Entered on [make.fun](https://make.fun/?ref=tv86zvxh&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
