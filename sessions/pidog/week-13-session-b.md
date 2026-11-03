# Week 13, Session B: Meet the Raspberry Pi 5

**Route:** PiDog  
**Time:** About 60 minutes. You may split it across days.  
**Guide:** Open [SunFounder — PiDog setup guide](https://docs.sunfounder.com/projects/pidog/en/latest/python/python_start/quick_guide_on_python.html) and the printed PiDog V2 guide. Follow the printed V2 guide for assembly and power.

## Before starting

- [ ] Complete the [previous session](../pidog/week-13-session-a.md), or repeat it if the checkpoint was difficult.
- [ ] Have ready: PiDog V2 kit, Raspberry Pi 5, 32 GB or larger microSD, official 27 W USB-C desk power supply, computer and microSD reader.
- [ ] Parent preparation: Make sure the Pi starts and the saved script can be reopened.

## During the session

1. **Recall (5 min):** Look at what you made in Session A and ask what should happen next.
2. **Build or change (40 min):** Write a tiny program that prints `sit`, `stand` or `stop` based on a typed choice. Run all three choices.
3. **Check (10 min):** Run, demonstrate or inspect the result. Ask what changed and what stayed the same.
4. **Record (5 min):** Write or draw the result and one idea for next time.

If he needs a starting point, type this together into `dog_choices.py` and let him change one response:

```python
choice = input("Choose sit, stand, or stop: ").strip().lower()
if choice in ("sit", "stand", "stop"):
    print(choice)
else:
    print("Try sit, stand, or stop")
```

Run it in the terminal with `python3 dog_choices.py`. This program only prints commands; the dog will move in later sessions.

## Finished when

He can open, edit and run a Python script on the Pi. If this takes longer, stop at a working point and continue next time.

If stuck: Pause at the last successful step in the V2 guide. For moving parts, stop and power off before inspecting them.

## Next

[Week 14, Session A](../pidog/week-14-session-a.md).
