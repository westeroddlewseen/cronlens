# cronlens

> Human-readable cron expression parser and schedule visualizer with next-run predictions.

---

## Installation

```bash
pip install cronlens
```

---

## Usage

```python
from cronlens import CronLens

lens = CronLens("0 9 * * 1-5")

print(lens.describe())
# → "At 09:00 AM, Monday through Friday"

print(lens.next_runs(count=3))
# → [
#     datetime(2024, 11, 18, 9, 0),
#     datetime(2024, 11, 19, 9, 0),
#     datetime(2024, 11, 20, 9, 0),
#   ]

lens.visualize()
# → Week schedule grid printed to terminal
```

You can also use the CLI:

```bash
cronlens "*/15 * * * *" --next 5
# Runs every 15 minutes
# Next 5 runs:
#   2024-11-18 14:15:00
#   2024-11-18 14:30:00
#   2024-11-18 14:45:00
#   2024-11-18 15:00:00
#   2024-11-18 15:15:00
```

---

## Features

- Parses standard and extended cron expressions
- Translates expressions into plain English descriptions
- Predicts upcoming run times
- Visualizes weekly and monthly schedules in the terminal

---

## License

This project is licensed under the [MIT License](LICENSE).