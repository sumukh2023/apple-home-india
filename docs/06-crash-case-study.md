# Case study: Home Assistant restarting itself

A debugging write-up from this project: what the symptoms were, how the cause was narrowed down, what was changed, and what remains unproven.

## Symptoms

- **Opening the automation editor crashed Home Assistant.** Starting a new automation in the UI showed "Connection lost", and Home Assistant restarted.
- **Unexplained restarts in the early morning**, even though the Raspberry Pi runs on a UPS.

**System:** Raspberry Pi 4 (4 GB RAM), Home Assistant OS, about 45 Apple Home accessories, plus a robot vacuum integrated through the community [Dreame Vacuum](https://github.com/Tasshack/dreame-vacuum) integration (installed with HACS).

## Hypotheses

| Hypothesis | How it was checked | Result |
|---|---|---|
| Power loss or under-voltage | Pi on a UPS; Raspberry Pi power-supply checker history | Ruled out: no under-voltage recorded in the 10 days reviewed |
| Corrupt automation file breaking the editor | Configuration check | Ruled out: configuration valid |
| A heavy integration exhausting memory | Memory profiling (below) | **Most likely cause** |

## Method

Home Assistant's own crash looked like a process being killed rather than an error being raised: no traceback, just a restart. On a 4 GB Pi that points to memory exhaustion.

A short script reproduced what the automation editor does when it opens, while sampling Home Assistant's memory and CPU use every second through the Supervisor API. It replayed the editor's requests one at a time, six seconds apart, so any spike could be pinned to a single request:

1. the blueprint list
2. integration descriptions and the full service list
3. trigger, condition and service icons
4. trigger and condition platform subscriptions
5. the triggers available for the robot vacuum
6. finally, the vacuum's **map camera image**

The integration exposes several **map camera** entities that render the vacuum's floor plan to images. Rendering a detailed multi-floor map is expensive, and the editor loads entity information for every device, including those cameras.

## Finding

The vacuum's **map cameras** were identified as the most likely cause: rendering them on demand can push Home Assistant's memory use over the limit, and the operating system then kills and restarts it.

Two observations fit:

- The automation editor requests information about every entity, and opening it triggered the crashes.
- The vacuum is scheduled to clean at **06:30 every day**. While it cleans, its map changes continuously and the map cameras keep re-rendering. That matches the **early-morning** restarts.

> **What remains unproven:** the exact chain *editor → camera render → out of memory* was inferred from these observations and the profiling, not caught in a single reproduction. That is why the result is being monitored rather than declared fixed.

## Fix

The two map camera entities that were enabled were **disabled** (Settings → Entities → camera → Disable). The vacuum itself, its controls, sensors and cleaning schedule are unaffected (238 of its 243 entities remain enabled); only the rendered map images are gone from Home Assistant. The vacuum's own app still shows the map.

## Result

| | After the fix |
|---|---|
| Home Assistant memory use at steady state | about 585 MB of 3.98 GB available (15 %) |
| Map cameras | Disabled |
| Monitoring | A stability review one week after the fix (restarts, memory peaks) |

## Lessons

1. **On a small computer, memory is the first suspect** for silent restarts: a process killed for running out of memory leaves no error message.
2. **Pin spikes to single actions.** Replaying one request at a time with a gap between them turns "it crashes sometimes" into "this request costs this much".
3. **Some entities are more expensive than they look.** Image-rendering entities (maps, camera snapshots) can cost far more than everything else in the system. Disable what you don't use.
4. **Correlate with schedules.** The morning restarts only made sense once they were lined up with the vacuum's 06:30 cleaning schedule.
5. **Separate what's proven from what's inferred**, and keep monitoring until the inferred part is confirmed.

## References

- [Dreame Vacuum integration](https://github.com/Tasshack/dreame-vacuum) by Tasshack: the community integration whose map camera entities are discussed here
- Home Assistant: [Supervisor API, `/core/stats`](https://developers.home-assistant.io/docs/api/supervisor/endpoints/) (used to sample memory and CPU) · [Raspberry Pi Power Supply Checker](https://www.home-assistant.io/integrations/rpi_power/)
