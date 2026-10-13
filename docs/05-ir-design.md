# IR and RF design

How infrared ACs and fans and RF curtains, devices that can't report anything back, become dependable Apple Home accessories.

## The constraint: one-way control

An IR or RF remote only **sends**. The AC never confirms what it received, and Home Assistant can't ask it what state it's in. Everything below follows from that:

1. **Home Assistant remembers state** that the appliance can't report.
2. **Commands carry complete states** wherever possible, so a single missed or repeated command can't leave the appliance in a half-changed state.
3. **Commands are applied strictly in order.**

## ACs: a thermostat with nothing to measure

### Why a thermostat entity

Apple Home's thermostat tile is the natural control for an AC: mode, target temperature, current temperature. Home Assistant's `generic_thermostat` produces a proper `climate` entity that the HomeKit Bridge exposes as exactly that tile. But a generic thermostat expects to *control* something based on a *measured* temperature. Two small tricks repurpose it:

| Part | What it is | Why |
|---|---|---|
| Dummy heater | A template switch whose on/off actions do nothing | `generic_thermostat` requires a switch to drive. This one is never used. |
| Virtual room temperature | A template sensor that always equals the setpoint | With room temperature = setpoint and zero tolerances, the thermostat never tries to act on its own. |
| `ac_mode: true` | Cool-only | Matches what the learned codes do. |

The real work is done by the **`ir_ac_bridge` blueprint**, which watches the thermostat and sends learned commands.

### Full-state commands

Most AC remotes don't send "temperature up". Every button press sends the **whole state**: power, mode, temperature, fan speed. So each learned command is a complete snapshot (`bedroom_ac_22` = on, cool, 22 °C), and:

- A missed command is fixed by the next one, with no accumulated error.
- Sending the same command twice is harmless.
- It works for any AC, whether or not Tuya's library recognises the brand, because nothing is decoded: the signal is replayed exactly as the AC's own remote produced it.

### The blueprint's rules

| Apple Home action | Command sent |
|---|---|
| Mode → Cool | `<prefix>_on`: the power-on state, at the power-on temperature (e.g. 24 °C) |
| Mode → Off | `<prefix>_off`, then the setpoint is reset to the power-on temperature |
| Temperature changed while cooling | `<prefix>_<temp>` (rounded to whole °C); the power-on temperature uses `<prefix>_on` |
| Temperature changed while off | Nothing; the AC stays off |

**Why reset the setpoint on Off?** `<prefix>_on` always powers the AC on at the power-on temperature. Resetting the slider when the AC turns off keeps Apple Home showing what the AC will actually do on the next power-on.

**Why `queued` mode?** That reset is itself a temperature change and re-triggers the blueprint. Queued runs execute in order: the second run sees the mode is already Off and does nothing. With `restart` mode, the reset could cancel the run that sent the Off command.

## Fans: five speeds from one slider

| Apple Home | Home Assistant | Command |
|---|---|---|
| Speed slider 1–100 % | Rounded up to 5 steps: 1–20 % → 1, 21–40 % → 2, … 81–100 % → 5 | `<fan>_speed_<n>` (most IR fans also turn on when a speed is pressed) |
| Off | Power helper → off; last speed **kept** | `<fan>_power_off` |
| On | Power helper → on; last speed resent (20 % if none) | `<fan>_speed_<last>` |

Dragging the slider in Apple Home sends a burst of updates. The template fan hands each one to a single **queued** script and returns at once, so every update is applied in order instead of being dropped as "already running", and the fan ends at the speed the slider stopped on.

Fan power is often a **toggle** (one button for on and off). The design therefore never sends power twice: turning on uses a speed command, and off is sent once.

## Curtains: RF with remembered position

RF curtain motors (433 MHz) can't report position either. A template cover sends `open` / `close` / `stop` and keeps an `is_open` helper, so Apple Home shows Open or Closed. RF commands are sent **twice**, about 0.3 s apart: open, close and stop are all safe to repeat, and the repeat covers an occasionally missed burst.

## `ir_send`: one sender for everything

Every IR and RF command goes through one script, `ir_send`, by name (`bedroom_ac_22`):

```
command "bedroom_ac_22"
   │
   ├─ prefix "bedroom_ac" listed in routes, and its blaster is online?
   │      └─ yes → Tuya Local sends the learned code over the LAN
   │
   └─ otherwise → fire the Smart Life scene "scene.bedroom_ac_22" through the cloud (if it exists)
```

This single seam makes the rest of the design independent of *how* commands travel:

- Appliances can move from cloud to local one at a time.
- A blaster that goes offline falls back to the cloud automatically.
- Errors are **not** swallowed. A command that was never learned stops with an error in the log instead of failing silently, which would make a tile look alive while doing nothing.
- It runs **queued**, so commands from different tiles can't overtake each other.

## Failure modes and mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Someone uses the physical remote | Home Assistant's remembered state drifts from reality | The next Apple Home command sends a full state and corrects it |
| A command is missed (obstruction, range) | Appliance doesn't change | Full-state AC commands self-correct on the next change; RF commands are sent twice |
| A blaster stops answering on the LAN | Commands can't go out locally | `ir_send` falls back to the cloud scene; an alert after 5 minutes; a power cycle fixes it ([07-local-control.md](07-local-control.md), section 5) |
| Home Assistant restarts mid-command | Command lost | Helpers and timers are restored; the next command applies a full state |

## Alternatives considered

| Approach | Why not (for this project) |
|---|---|
| Smart Life's built-in AC remote and Tuya's AC library | Only works when Tuya recognises the AC's remote; many models in Indian homes aren't recognised |
| Integrations that control the AC through Tuya's cloud AC API | Also depend on Tuya recognising the AC, and on the cloud |
| Community IR code databases | Need the exact model's codes in the right format; learning from the real remote always matches |
| A Broadlink or ESPHome IR blaster | Works well, but the Tuya blasters are cheaper, widely sold in India, and many homes already own them |

## References

- Home Assistant: [Generic Thermostat](https://www.home-assistant.io/integrations/generic_thermostat/) (the `ac_mode` and tolerance options) · [Template fan and cover](https://www.home-assistant.io/integrations/template/) · [Automation modes (`queued`, `restart`)](https://www.home-assistant.io/docs/automation/modes/) · [Scripts](https://www.home-assistant.io/integrations/script/) · [Remote: `send_command`, `learn_command`](https://www.home-assistant.io/integrations/remote/)
- [Tuya Local](https://github.com/make-all/tuya-local) by make-all and contributors: sends and learns the IR/RF codes
