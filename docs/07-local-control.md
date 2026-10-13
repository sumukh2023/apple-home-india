# Moving an existing cloud setup to local control

For anyone who already runs Tuya devices through the Tuya cloud (the official Tuya integration, remotes learned in Smart Life, scenes fired through the cloud) and wants everything to run over the home network instead, **without rebuilding from scratch and without breaking Apple Home**.

Starting fresh? Follow [04-setup-guide.md](04-setup-guide.md) instead: it is local from day one.

> **Credit.** Local control in this project is made possible by **[Tuya Local](https://github.com/make-all/tuya-local)** by make-all and its contributors: the Home Assistant integration that talks to Tuya devices directly on your network, including IR/RF blasters. See [Credits](#9-credits).

---

## 1. What changes, and what doesn't

| | Before (cloud) | After (local) |
|---|---|---|
| Path of a command | Home Assistant → internet → Tuya cloud → device | Home Assistant → home Wi-Fi → device |
| Works without internet | No | Yes |
| Typical response time | ~0.7 s | ~0.35 s |
| Apple Home tiles, rooms, scenes | — | Unchanged, if you follow the swap steps below |
| Automations | — | Unchanged: entity IDs are kept |
| Tuya developer account | Not needed | Needed **only** to export IR/RF codes you already learned in Smart Life (section 4B). Not needed for anything else. |

## 2. Before you start

1. **Back up** Home Assistant (Settings → System → Backups) and download the backup.
2. **Reserve the IP address** of every Tuya device in your router (see [04-setup-guide.md, section 2](04-setup-guide.md#2-prepare-your-network)). Do this *before* any router reboot: a reboot can move devices to new addresses.
3. Install **Tuya Local** from HACS and restart Home Assistant.

## 3. Switches, plugs and geysers

No developer account is needed. Do one device at a time.

### 3.1 Add the device to Tuya Local

**Settings → Devices & services → Add integration → Tuya Local → Smart Life (cloud-assisted)**, enter your Smart Life user code, scan the QR code, pick the device, confirm its IP and choose the suggested profile. Name it "… LOCAL".

### 3.2 Check which local channel is which

For multi-gang switches, toggle each new local channel and confirm that **only** the matching existing (cloud) entity changes. Channel order does not always match the labels you gave in Smart Life.

### 3.3 Swap the entity IDs

Automations, dashboards and the HomeKit Bridge refer to entity IDs, so the local entity must take over the old ID:

1. Cloud entity → ⚙️ → rename its ID to `…_cloud` and **disable** it.
2. Local entity → ⚙️ → rename its ID to the old one.
3. Lights driven by a switch channel: recreate the **Change device type of a switch → Light** helper on the local switch, and give the new light the old light's ID.

### 3.4 Apple Home

An Apple Home accessory's identity is derived from the entity behind it, not its ID. After a swap, Apple Home may show the device as a **new** accessory: assign its room, re-add it to scenes, and remove the old tile.

<details>
<summary><b>Advanced: keep the existing Apple Home tile</b></summary>

The HomeKit Bridge stores which accessory number belongs to which entity in `/config/.storage/homekit.<entry_id>.aids`. To make the local entity inherit the old tile (room, scenes and automations kept):

1. Back up first.
2. Disable the HomeKit Bridge entry (Settings → Devices & services → HomeKit Bridge → ⋮ → Disable). This saves its state to disk.
3. In the `.aids` file, find the allocation key of the old cloud entity (`<platform>.<domain>.<unique_id>`, e.g. `tuya.switch.tuya.<id>switch_1`) and rename that key to the local entity's (`tuya_local.switch.<id>`), keeping the same number.
4. Re-enable the bridge. If the old entity had a different *device class* (e.g. switch vs outlet), set the same class on the local entity first (entity → ⚙️ → Show as), or Apple Home will see a different accessory type.

</details>

### 3.5 Safety-critical appliances (geysers)

For a geyser, an "off" that silently fails is dangerous, and a local connection can drop. The author's setup uses three layers:

1. **Keep the cloud entity enabled** (hidden, renamed `…_cloud`) instead of disabling it. The auto-off automation switches off through **both** the local and the cloud entity, each with `continue_on_error: true`, so either path can do it.
2. **Use the plug's own countdown** as a hardware backstop. Most Tuya plugs have a built-in countdown (Tuya Local exposes it as a `time.…_timer` entity). When the geyser turns on, set it a few minutes longer than the Home Assistant timer; the plug then switches itself off even if Home Assistant, the Pi or Wi-Fi is down. Set it back to `00:00:00` when the geyser turns off.
3. **Set the plug's power-on behaviour to off**, so a geyser doesn't come back on by itself after a power cut.

```yaml
# When the geyser turns on (in addition to starting the HA timer):
- action: time.set_value
  continue_on_error: true
  target:
    entity_id: time.bedroom_geyser_local_timer
  data:
    time: "01:05:00"   # HA timer is 1 h; the plug cuts off 5 min later if HA didn't
```

## 4. IR and RF appliances (ACs, fans, curtains)

Your existing Smart Life scenes keep working throughout. Choose how to get the codes into Home Assistant:

| | **A. Re-learn locally** | **B. Export what Smart Life already learned** |
|---|---|---|
| Developer account | No | Yes (free trial tier is enough) |
| Needs the physical remotes | Yes | No |
| Effort | One button press per command | About an hour, mostly setup |
| Best when | You have the remotes and a modest number of commands | You learned many commands (e.g. a full AC temperature range) or lost the remotes |

### 4A. Re-learn locally

Add each blaster to Tuya Local (profile `basic_ir_remote` or an exact match), then follow [04-setup-guide.md, section 5](04-setup-guide.md#5-learn-your-remotes-in-home-assistant). Name each command after the scene it replaces (`bedroom_ac_22` for `scene.bedroom_ac_22`), so `ir_send` can fall back to that scene automatically.

### 4B. Export existing codes with a Tuya developer account

1. **Create the project.** Sign up at [platform.tuya.com](https://platform.tuya.com) → **Cloud → Development → Create Cloud Project**: development method **Smart Home**, and the **data center where your Smart Life account lives**. This is decided by the account's region, not where you live. In Home Assistant, the official Tuya integration's device diagnostics show an `endpoint` field: `tuyaus.com` means **Western America**, `tuyaeu.com` **Central Europe**, `tuyain.com` **India**, `tuyacn.com` **China**. The wrong data center gives an empty device list.
2. **Add the IR service.** Keep the default services and add **IR Control Hub Open Service** (or subscribe to it under Cloud Services and authorize it for the project).
3. **Link your Smart Life account.** Project → **Devices → Link Tuya App Account → Add App Account**, and scan the QR code from Smart Life (Me → scan icon). Your IR blasters should appear in the device list.
4. **Read the codes.** These calls are read-only. [tinytuya](https://github.com/jasonacox/tinytuya)'s `Cloud` class can make them with your project's Access ID and Secret:

   | Call | Returns |
   |---|---|
   | `GET /v2.0/infrareds/{blaster_id}/remotes` | The remotes under each blaster |
   | `GET /v2.0/infrareds/{blaster_id}/remotes/{remote_id}/learning-codes` | Every learned code: `key`, `key_name`, `code` |
   | `GET /v1.1/homes/{home_id}/scenes` | Every Tap-to-Run scene, with the remote (`entity_id`) and button (`keyId`) it presses |

   Joining the scenes to the learned codes gives an exact *scene → code* table.
5. **Convert the codes** to the format Tuya Local sends:
   - **IR:** the `code` is a hex string of 16-bit little-endian pulse durations in microseconds. Convert with tinytuya: `IRRemoteControlDevice.pulses_to_base64(IRRemoteControlDevice.hex_to_pulses(code))`, and send it as `b64:<result>`.
   - **RF:** the `code` is JSON. Its `key1.code` value is exactly what Tuya Local's RF sender expects. Send it as `rf:<value>`.
6. **Store them.** Either put them in the `routes` of `ir_send` as raw `b64:`/`rf:` commands, or write them into Tuya Local's code store (`/config/.storage/tuya_local_remote_<blaster_id>_codes`, format `{"version": 1, "minor_version": 1, "key": "<filename>", "data": {"<device>": {"<command>": "<code>"}}}`).
   > Home Assistant reads `.storage` **only at start-up**. A code file written while it's running is invisible until the next restart; until then every send fails with "command not found". Restart after writing, or use inline codes.
7. Once the codes work locally, nothing depends on the developer project any more. You can let its trial lapse.

**Buttons that were never learned** (taken from Tuya's built-in brand library instead of being learned) cannot be exported: the library returns encrypted codes. Two ways round it:

- If you learned the same button on **another remote of the same model** (common with several identical fans), decode both to check they match (`IRRemoteControlDevice.pulses_to_nec`) and reuse that code.
- Otherwise, re-learn that button locally (4A).

### 4C. Send locally, fall back to the cloud

Copy [`packages/examples/ir_send.example.yaml`](../packages/examples/ir_send.example.yaml) and point every AC, fan and curtain action at `script.ir_send` (the repo's blueprint and examples already do). For each command it sends locally when the blaster is reachable, and fires the original Smart Life scene when it isn't. During migration, appliances not yet listed in `routes` simply keep using their scenes.

Two rules:

- **Never send the same command both locally and through the cloud.** IR fan power is usually a toggle (two sends cancel out), and late-arriving cloud copies can re-order commands (open → stop → *open again*). Use the cloud only as a fallback.
- **Don't hide send errors.** If the local send fails with `continue_on_error`, the tile looks alive but does nothing, and the fallback never runs. Let errors surface.

### 4D. Exclude the blasters from Apple Home

Tuya Local creates a `remote.` entity per blaster. If your HomeKit Bridge includes the `remote` domain, the blasters appear as tiles after the next restart, and switching one "off" stops it sending. Add every blaster to the bridge's **exclude** list. Hiding the entity isn't enough.

## 5. When a blaster stops answering locally

Some cheap Tuya IR blasters stop accepting local connections (they don't even answer ping) while staying online in the Smart Life app. In the author's home all four units of one model were found in this state (shortly after a router reboot had changed their IP addresses, though the exact cause isn't certain); a newer IR + RF model was unaffected. A 10-second power cycle fixed each one.

What limits the damage:

- **Reserved IP addresses**, so a router reboot doesn't move devices.
- **Tuya Local keeps a permanent connection** to each blaster and marks it unavailable when it stops responding, so `ir_send` falls back to the cloud scenes.
- **An alert** when a local device has been unavailable for 5 minutes:

```yaml
automation:
  - id: tuya_local_unavailable_alert
    alias: Tuya Local device unavailable
    triggers:
      - trigger: state
        entity_id:
          - remote.bedroom_ir_blaster_local
          - switch.bedroom_switches_local_switch_1
        to: unavailable
        for: "00:05:00"
    actions:
      - action: persistent_notification.create
        data:
          title: Local device unreachable
          message: >-
            {{ state_attr(trigger.entity_id, 'friendly_name') }} has been unreachable
            for 5 minutes. Unplug it for 10 seconds to restart it.
```

If the internet is also down, a stalled blaster's appliances won't respond until it is power-cycled. For a hands-off fix, power each blaster from its own local smart plug and let an automation power-cycle it when it goes unavailable.

## 6. Gotchas

| Problem | Cause | Fix |
|---|---|---|
| "Already in progress" when adding a device | An earlier setup attempt timed out and is still holding the device | Restart Home Assistant and add it again |
| Tuya Local asks for the QR code again | Its Smart Life sign-in ends when Home Assistant restarts | Scan a new code; devices already added are unaffected |
| A device offers only unrelated profiles (pet feeders, locks…) | It reports too little locally for Tuya Local to identify it (seen on some single-function Wi-Fi sockets) | Keep it on the cloud, or replace it with a model Tuya Local supports |
| Old devices listed under **Discovered** | Tuya Local hears devices you haven't added | Ignore them; they can still be added later |
| Tiles control the right device but show "No Response" after a restart | Apple Home received new accessories | See section 3.4 |

## 7. Results in the author's home

| | Count |
|---|---|
| Light channels moved from cloud to local | 22 |
| Plugs and geysers moved to local | 3 |
| IR blasters on local control | 5 |
| ACs, fans and curtains on local control (with cloud fallback) | 11 |
| Smart Life scenes replaced by local codes | 115 of 115 (106 exported directly, 9 reused from an identical fan model's learned codes) |
| Median command latency | 0.35 s local vs 0.67 s cloud |

Everything except one Wi-Fi socket that Tuya Local can't identify now runs with no internet connection.

## 8. Rolling back

Everything above is reversible: re-enable the `…_cloud` entities and give them their original IDs back, or restore the backup from section 2. The Smart Life scenes are never modified.

## 9. Credits

- **[Tuya Local](https://github.com/make-all/tuya-local)** by make-all and contributors: local control of Tuya switches, plugs and IR/RF blasters in Home Assistant, including learning and sending remote codes. The local half of this project is built entirely on it.
- **[tinytuya](https://github.com/jasonacox/tinytuya)** by Jason Cox and contributors: the Tuya cloud API client and IR code conversion used to export learned codes.
- **[Home Assistant](https://www.home-assistant.io)** and its [HomeKit Bridge](https://www.home-assistant.io/integrations/homekit/), [Remote](https://www.home-assistant.io/integrations/remote/) and [Change device type of a switch](https://www.home-assistant.io/integrations/switch_as_x/) integrations.
- **Tuya Developer documentation**: [IR Control Hub Open Service](https://developer.tuya.com/en/docs/cloud/ir-control-hub-open-service?id=Kb3oe2mk8ya72) · [Get Learning Codes](https://developer.tuya.com/en/docs/cloud/5c93c9ffc5?id=Kb3oebi2lvz0k).
- **[HACS](https://hacs.xyz)**: how Tuya Local is installed.
