# Setup guide

How to build this system from scratch: affordable Tuya devices (switches, plugs, IR and RF blasters) and IR-only appliances (ACs, ceiling fans, curtains), all controlled natively from Apple Home through Home Assistant, **entirely over your home network**.

**You will end up with:** every light, switch, plug and geyser, every AC, fan and curtain, working from Apple Home and Siri even when the internet is down. Each AC is a real thermostat tile, each IR fan has power and 5 speeds, RF curtains have open / close / stop, and geysers have a restart-safe auto-off.

**Time:** one weekend. **Skill:** comfortable following instructions and editing YAML files. No programming needed.

**How to use this guide:** work through the sections in order and finish each one before starting the next. Most sections end with a quick test, so problems show up where they start. Section 14 lists the common problems and their fixes.

### Words used in this guide

| Term | Meaning |
|---|---|
| **Home Assistant** | The free home-automation software that runs on the Raspberry Pi and connects everything |
| **Integration** | A Home Assistant plug-in that talks to a kind of device or service (Tuya Local, HomeKit Bridge, …). Added under **Settings → Devices & services** |
| **App** | Extra software that runs alongside Home Assistant (a file editor, a file share). Called *add-ons* before Home Assistant 2026.2. Found under **Settings → Apps** |
| **Entity** | One controllable or readable thing in Home Assistant: a light, a switch, a thermostat, a sensor |
| **Entity ID** | An entity's internal name, e.g. `light.bedroom_ceiling` or `remote.bedroom_ir_blaster_local`. Find any entity's ID under **Settings → Devices & services → Entities** (search, open it, ⚙️) |
| **Helper** | An entity you create yourself to remember something (a timer, an on/off flag) |
| **YAML** | The text format Home Assistant's configuration files use. **Indentation (spaces) matters**: copy examples exactly and never use tabs |
| **Package** | A YAML file that bundles everything for one appliance (its entities, helpers and automation) |
| **Blueprint** | A reusable automation recipe; you fill in a few inputs |
| **HACS** | The Home Assistant Community Store, used to install community integrations such as Tuya Local |
| **Local key** | A per-device password Home Assistant needs to talk to a Tuya device directly over your network |

---

## 0. Before you start

### Prerequisites checklist

**For Home Assistant** (from the [official Raspberry Pi installation guide](https://www.home-assistant.io/installation/raspberrypi/)):

- [ ] Raspberry Pi 4 or 5 (this project uses a Pi 4 with 4 GB; 2 GB is the stated minimum)
- [ ] microSD card, **32 GB or larger**, Application Class 2 (A2) recommended
- [ ] A power supply made for the Pi (not a phone charger or a computer's USB port)
- [ ] An Ethernet cable to the router (required during installation)
- [ ] A computer with an SD card reader (built in, or a cheap USB adapter) and [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [ ] Recommended: a small UPS for the Pi
- [ ] A free **GitHub account** (HACS uses it to download community integrations)

**For the home:**

- [ ] A Wi-Fi router with a **2.4 GHz** network and **DHCP / address reservation** (most routers and mesh systems, e.g. Deco, have it)
- [ ] Tuya devices for the rooms you want to control (see [03-bill-of-materials.md](03-bill-of-materials.md)): switch modules, smart plugs, and one Wi-Fi IR blaster per room with IR appliances (an IR + RF blaster for RF curtains)
- [ ] The **original remotes** for every AC, fan and curtain (codes are learned from them)
- [ ] For geysers: a smart plug rated **16 A** (a geyser draws far more than a 10 A plug is built for)

> ⚠️ **Electrical safety.** Wi-Fi switch modules are wired into your switchboards on mains power. Have a **licensed electrician** install them, with the circuit's MCB switched off. Smart plugs and IR blasters just plug in.

**For Apple Home:**

- [ ] An iPhone or iPad with the **Home** app, on the same Wi-Fi as the Pi
- [ ] Recommended: an Apple TV or HomePod as a [home hub](https://support.apple.com/en-in/102557), needed for Apple Home automations and control away from home

**Accounts:**

| Account | Needed for | Cost |
|---|---|---|
| Apple ID with an Apple home hub (Apple TV or HomePod) | Apple Home automations and control away from home | Hardware only |
| Smart Life app account | Pairing Tuya devices to Wi-Fi, and a one-time sign-in so Home Assistant can fetch each device's local key | Free |

No Tuya developer account is needed. After setup, nothing depends on the Tuya cloud.

> **Already set up through the Tuya cloud** (remotes learned in Smart Life, scenes firing through the cloud)? Section 12 explains how to keep those scenes as a backup, and `07-local-control.md` explains how to move an existing cloud setup to local without starting over.

---

## 1. Install Home Assistant OS on the Raspberry Pi

Follow the [official guide](https://www.home-assistant.io/installation/raspberrypi/); in short:

1. On your computer, open **Raspberry Pi Imager** and choose **OS → Other specific-purpose OS → Home automation → Home Assistant**, then the image for your board (Raspberry Pi 4 or 5).
2. Write it to the microSD card, put the card in the Pi, connect the Pi to your router **with an Ethernet cable**, and power it on.
3. Wait: the first start can take **up to 20 minutes**. Then open `http://homeassistant.local:8123` in a browser on the same network. If that page doesn't load, find the Pi's IP address in your router app's list of connected devices and open `http://<that IP>:8123` instead.
4. Complete onboarding: create your user, and set your **home location and time zone** correctly (schedules and timers depend on it).
5. Install any updates Home Assistant offers (they appear at the top of **Settings**).
6. Put the Pi on a UPS if you can. Power cuts corrupt SD cards; a UPS also keeps automations such as geyser cut-offs running.

## 2. Prepare your network

Home Assistant reaches each Tuya device by its IP address, so addresses must never change.

1. In your router app (Deco, TP-Link, JioFiber, Airtel, etc.), find **Address Reservation** / **DHCP reservation**.
2. Reserve the current IP of the Raspberry Pi.
3. Reserve the IP of **every Tuya device** as you add it (step 4). Find a device's MAC address in Smart Life: open the device → ✏️ → **Device Information**.
4. Tuya devices use **2.4 GHz** Wi-Fi only. If your router has a separate "IoT network" or guest network, keep Tuya devices on the **main** network so Home Assistant can reach them.

> If the router is rebooted before addresses are reserved, devices can move to new IPs and drop off local control. Reserving them prevents this.

## 3. Pair your devices in Smart Life

Pair every switch, plug and IR blaster in the **Smart Life** app as you normally would (**+ → Add Device**, then follow the app; keep your phone near the device and use your **2.4 GHz** Wi-Fi), and give each one a clear name ("Bedroom Switches", "Bedroom IR Blaster"). This only connects them to your Wi-Fi.

Place each IR blaster where it has a clear line of sight to the AC and fan it controls, as you would point a remote.

**You do not need to add remotes or scenes in Smart Life.** Remotes are learned in Home Assistant in step 5.

## 4. Add your devices to Home Assistant with Tuya Local

[Tuya Local](https://github.com/make-all/tuya-local) talks to Tuya devices directly over your network. It signs in with your Smart Life account once, to fetch each device's local key; after that, control is entirely local.

### 4.1 Install

1. **Install HACS** (full instructions: [hacs.xyz](https://hacs.xyz/docs/use/download/download/)):
   1. **Settings → Apps → Install app → ⋮ → Repositories**, add `https://github.com/hacs/addons`.
   2. Install and **Start** the **Get HACS** app, open its **Log** tab and follow the instructions there, then restart Home Assistant (**Settings → ⋮ → Restart Home Assistant**).
   3. **Settings → Devices & services → Add integration → HACS**. Home Assistant shows a code: open `github.com/login/device`, sign in to GitHub, enter the code and authorize HACS. If HACS isn't in the list, refresh the browser page first.
2. Open **HACS** from the sidebar, search for **Tuya Local**, select **Download**, and restart Home Assistant.

### 4.2 Add each device

1. In Smart Life: **Me → ⚙️ Settings → Account and Security → User Code**. Copy it.
2. In Home Assistant: **Settings → Devices & services → Add integration → Tuya Local → Smart Life (cloud-assisted)**, enter the user code, and scan the QR code with Smart Life.
3. Pick a device, confirm its IP address (reserve it in your router now), and choose the **device profile** Tuya Local suggests:
   - Switches and plugs: prefer an exact product match; for plain switch modules `simple_switch`, `simple_dual_switch` or the matching multi-gang profile works.
   - IR blasters: an exact product match if offered, otherwise `basic_ir_remote`.
4. Name it clearly, e.g. "Bedroom Switches LOCAL", "Bedroom IR Blaster LOCAL". An IR blaster appears as a `remote.` entity, e.g. `remote.bedroom_ir_blaster_local`. Note each blaster's entity ID (**Settings → Devices & services → Entities**, search `remote.`): you will use it in steps 5 and 6.
5. Test each switch and plug from its device page before moving on.
6. For switch channels that drive lights, Apple Home should see a **light**: **Settings → Devices & services → Helpers → Create helper → Change device type of a switch → Light**.

### 4.3 Things to know

- A Tuya device accepts **one local connection** at a time. Home Assistant holds it; the Smart Life app still works through the cloud.
- The Smart Life sign-in used by Tuya Local **expires when Home Assistant restarts**. Devices already added keep working; you only scan a new QR code when adding more devices.
- Tuya Local lists other Tuya devices it hears on the network under **Discovered**. Ignore the ones you don't want to add.

## 5. Learn your remotes in Home Assistant

Each button press is learned once and stored by Tuya Local under a **device** name (the appliance, e.g. `bedroom_ac`) and a **command** name (the button, e.g. `22`). Together they form the command `<device>_<command>` (e.g. `bedroom_ac_22`) that the blueprints and examples use.

### 5.1 How to learn one command

1. Go to **Developer tools → Actions**, choose **Remote: Learn command**, switch to YAML mode and enter (adjust the names):

   ```yaml
   action: remote.learn_command
   target:
     entity_id: remote.bedroom_ir_blaster_local
   data:
     device: bedroom_ac
     command: "22"
   ```

2. Click **Perform action**. A notification (🔔, bottom of the sidebar) asks you to press the button. Within **30 seconds**, point the original remote at the blaster from about 30 cm away and press it once.
3. Check it: run **Remote: Send command** with the same names. The appliance should respond:

   ```yaml
   action: remote.send_command
   target:
     entity_id: remote.bedroom_ir_blaster_local
   data:
     device: bedroom_ac
     command: "22"
   ```

Learning the same command again overwrites it, so a bad recording is easy to redo.

Quote numeric command names (`"22"`), and keep every name lower-case with underscores.

### 5.2 What to learn

| Appliance | Device name | Commands to learn | How |
|---|---|---|---|
| AC | `bedroom_ac` | `on`, `off`, `16` … `30` | AC remotes send the **whole state** with every press, so learn each one in **cool** mode. **`on`:** set the remote to cool at your preferred power-on temperature (e.g. 24 °C) while it shows off, start learning, press **power**. **Temperatures:** start learning, then press up or down so the remote lands on that temperature (e.g. from 21, press up to reach `22`). Skip the number that equals your power-on temperature: `on` covers it. **`off`:** start learning, press **power** while the remote shows on. |
| Ceiling fan | `bedroom_fan` | `power_off`, `speed_1` … `speed_5` | Press the matching button. Pressing a speed also turns most IR fans on. |
| RF curtain | `bedroom_curtain` | `open`, `close`, `stop` | Add `command_type: rf` to the learn action (below). |

For RF, the learn action is:

```yaml
action: remote.learn_command
target:
  entity_id: remote.bedroom_ir_blaster_local
data:
  device: bedroom_curtain
  command: open
  command_type: rf
```

> **RF learning depends on the blaster.** IR learning works on Tuya IR blasters in general, but not every IR + RF blaster supports RF learning over the local network. If yours times out on RF, learn that curtain in Smart Life instead (section 12): `ir_send` then sends it through the cloud automatically.

## 6. Add the files from this repository

You need a way to edit files in Home Assistant's `/config` folder. Install one of these apps from **Settings → Apps → Install app**:

- **File editor**: edit files in the browser, inside Home Assistant.
- **[Samba share](https://github.com/home-assistant/addons/blob/master/samba/DOCS.md)**: opens `/config` as a network folder on your computer (Finder → Go → Connect to Server, or File Explorer on Windows), so you can copy this repository's files across directly.

**Get this repository's files** onto your computer: on the repository's GitHub page, select **Code → Download ZIP**, then unzip it. The folders below (`blueprints/`, `packages/examples/`) are inside.

Then:

1. Add the two blueprints. The quickest way is the import buttons: each opens your Home Assistant at its blueprint import screen, then select **Preview** and **Import blueprint**.

   [![Import the IR AC bridge blueprint into Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fsumukh2023%2Fapple-home-india%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsumukh2023%2Fir_ac_bridge.yaml) [![Import the appliance safety timer blueprint into Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fsumukh2023%2Fapple-home-india%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsumukh2023%2Fappliance_safety_timer.yaml)

   Or copy the folder `blueprints/automation/sumukh2023/` into `/config/blueprints/automation/`. Either way the blueprints end up at `/config/blueprints/automation/sumukh2023/ir_ac_bridge.yaml` and `…/appliance_safety_timer.yaml`, which is the path the examples use.
2. Create a `/config/packages/` folder and add to `configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   If `configuration.yaml` already has a `homeassistant:` line, add only the `packages:` line underneath it (indented by two spaces). A second `homeassistant:` line would break the configuration.

3. Copy `packages/examples/ir_send.example.yaml` to `/config/packages/ir_send.yaml`. Under `routes`, list every device name from step 5 with the blaster that sends it:

   ```yaml
   routes:
     bedroom_ac: {remote: remote.bedroom_ir_blaster_local, repeats: 1}
     bedroom_fan: {remote: remote.bedroom_ir_blaster_local, repeats: 1}
     bedroom_curtain: {remote: remote.bedroom_ir_blaster_local, repeats: 2}
   ```

   Delete the example lines for appliances you don't have. Every AC, fan and curtain command goes through this one script. It sends the learned code locally; if the blaster is offline it falls back to a Smart Life scene of the same name, if you created one (section 12).

4. Copy the examples you need from `packages/examples/` into `/config/packages/`, renamed per room (sections 7–10).
5. **Developer tools → YAML → Check configuration**. If it reports an error, it names the file and line: almost always a wrong indent or a name not replaced. Fix it, check again, then restart Home Assistant (**Developer tools → YAML → Restart**).

## 7. ACs as Apple Home thermostats

Uses `packages/examples/ir_ac.example.yaml` and the `ir_ac_bridge` blueprint.

1. Copy `ir_ac.example.yaml` to `packages/bedroom_ac.yaml` (one file per AC).
2. Replace every `bedroom_ac` / `Bedroom AC` with your AC's device name from step 5.
3. Set `power_on_temperature` in the file to the temperature your `on` command sends (e.g. `24`).
4. Check configuration, restart, and test: set the thermostat to **Cool**, change the temperature, then turn it **Off**.

Apple Home shows a cool-only thermostat. The room temperature it shows is a placeholder that mirrors the setpoint, because an IR AC cannot report the real temperature.

## 8. Ceiling fans with 5 speeds

Uses `packages/examples/fans.yaml` (copy once) and `packages/examples/ir_fan.example.yaml` (copy once per fan).

1. Copy `fans.yaml` to `packages/fans.yaml` unchanged.
2. Copy `ir_fan.example.yaml` to `packages/bedroom_fan.yaml` and replace every `bedroom_fan` / `Bedroom Fan` with your fan's device name.
3. Check configuration, restart, and test power and each speed.

The fan remembers its last speed while off, and fast slider drags in Apple Home are applied in order.

## 9. RF curtains

Uses `packages/examples/rf_curtain.example.yaml`.

1. Copy it to `packages/bedroom_curtain.yaml` and replace every `bedroom_curtain` / `Bedroom Curtains` with your curtain's device name.
2. Check configuration, restart, and test open, stop and close.

RF motors cannot report their position, so Home Assistant remembers whether the curtain was last opened or closed.

## 10. Geyser safety cut-off

Uses `packages/examples/appliance_safety_timer.example.yaml` and the `appliance_safety_timer` blueprint.

1. Copy the example to `packages/bedroom_geyser.yaml`. Replace `switch.bedroom_geyser` with your geyser plug's entity ID (from step 4), and set the maximum on-time in both places (the timer's `duration` and `max_on_time`). If the plug is on Tuya Local, fill in `backup_switch` and `hardware_countdown` as described in [07-local-control.md](07-local-control.md), section 3.5; otherwise delete those two lines. Use a **16 A** plug for a geyser.
2. In Home Assistant, open the plug's device page (**Settings → Devices & services → Tuya Local →** your plug) and, under **Configuration**, set its **power-on behaviour** (it may be called *initial state*) to **off**. After a power cut the geyser then stays off instead of switching back on by itself.
3. Test: turn the geyser on and confirm the countdown starts (and, if set, the plug's own timer shows the on-time plus 5 minutes); turn it off and confirm both are cancelled.

The countdown is restorable, so it survives Home Assistant restarts. After every start-up the blueprint waits a short grace period (`startup_grace`), then switches the appliance off if it is on with no countdown running.

## 11. Expose everything to Apple Home

1. **Settings → Devices & services → Add integration → HomeKit Bridge**. Choose **bridge** mode and include the domains you want (climate, fan, cover, light, switch, …).
2. In the bridge's **options**, **exclude** helper entities that should not become tiles:
   - every `switch.*_ac_dummy_heater`
   - every IR blaster (`remote.*_local` created by Tuya Local); a blaster tile switched off in Apple Home would stop that blaster sending commands
   - TV remotes and media players you don't want, robot-vacuum setting switches

   To change this later: **Settings → Devices & services → HomeKit Bridge → Configure**.
3. A notification in Home Assistant (🔔) shows a QR code and pairing code. In the **Home** app: **+ → Add Accessory**, scan the QR code (or **More options** and enter the code).
4. iOS warns that the bridge is an **Uncertified Accessory**. This is expected for Home Assistant: tap **Add Anyway**.
5. Assign each accessory to its room.

> An Apple Home accessory's identity comes from the Home Assistant entity behind it. If you later replace a device's entity, Apple Home may show it as a **new** accessory: re-assign its room, re-add it to scenes, and remove the old tile.

## 12. Optional: Smart Life scenes as a cloud backup

You can also learn an appliance in Smart Life and create one **Tap-to-Run scene** per command. `ir_send` fires that scene when the blaster can't be reached locally, or for any appliance that isn't listed in `routes` (for example a curtain your blaster can't learn over RF locally).

1. In Smart Life, add the remote under its blaster (a **DIY** remote if Smart Life doesn't recognise the brand) and learn the buttons.
2. Create a Tap-to-Run scene per command, named so its entity ID matches the command: `Bedroom AC 22` becomes `scene.bedroom_ac_22`, `Bedroom Fan Speed 3` becomes `scene.bedroom_fan_speed_3`.
3. Add Tuya's official cloud integration so the scenes appear in Home Assistant: **Settings → Devices & services → Add integration → Tuya**, enter your user code, scan the QR code.

Scenes run through the Tuya cloud, so they need internet. Locally learned commands don't.

## 13. Back up

1. **Settings → System → Backups**: create a backup and download it to your computer. Learned remote codes are included.
2. Download the [backup emergency kit](https://www.home-assistant.io/more-info/backup-emergency-kit/) (it holds the backup encryption key) and store it safely. Without it, backups cannot be restored.
3. Take a fresh backup after every significant change, especially after learning remotes.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| **Check configuration** reports an error | Wrong indentation, a tab character, a duplicated key (e.g. two `homeassistant:` lines), or a name not replaced | Go to the file and line it names; compare with the example. See **Settings → System → Logs** for details |
| `homeassistant.local:8123` doesn't open | Your network doesn't support `.local` names | Use the Pi's IP address from your router: `http://<IP>:8123` |
| A local device shows **unavailable** after a router reboot | Its IP changed | Find the new IP in the router, reserve it, and update the host in **Tuya Local → device → Configure** |
| An IR blaster shows **unavailable** in Home Assistant but still works in Smart Life | Some blasters stop answering on the local network after a while | Unplug it for 10 seconds |
| Learning times out | Remote too far or not aimed at the blaster; or RF without `command_type: rf` | Hold the remote about 30 cm from the blaster and retry; for curtains add `command_type: rf` |
| "Command … not found for …" in the log | That command was never learned, or the name differs | Learn it (step 5) with exactly the name the error shows |
| A tile does nothing and the blaster is offline | No Smart Life scene to fall back to | Power-cycle the blaster, or add a backup scene (section 12) |
| "Already in progress" when adding a Tuya Local device | A previous setup attempt is stuck | Restart Home Assistant, then add the device again |
| Home Assistant restarts when you open the automation editor | Memory exhaustion (e.g. a robot-vacuum map camera on a 4 GB Pi) | See `06-crash-case-study.md`; disable the map camera entities |

## 15. Final checklist

- [ ] Every Tuya device's IP is reserved in the router
- [ ] Every switch, plug, geyser and IR blaster is added through Tuya Local
- [ ] Every AC, fan and curtain command is learned and listed in `ir_send` routes
- [ ] Each AC: Cool, temperature change and Off all work from Apple Home
- [ ] Each fan: power and all 5 speeds work from Apple Home
- [ ] Each curtain: open, close and stop work
- [ ] Each geyser switches itself off at the end of its countdown
- [ ] Dummy heaters and IR blasters are excluded from the HomeKit Bridge
- [ ] A backup has been downloaded and the emergency kit stored safely

## References

- Home Assistant: [Raspberry Pi installation](https://www.home-assistant.io/installation/raspberrypi/) · [Packages](https://www.home-assistant.io/docs/configuration/packages/) · [Blueprints](https://www.home-assistant.io/docs/blueprint/) · [HomeKit Bridge](https://www.home-assistant.io/integrations/homekit/) · [Generic Thermostat](https://www.home-assistant.io/integrations/generic_thermostat/) · [Template](https://www.home-assistant.io/integrations/template/) · [Change device type of a switch](https://www.home-assistant.io/integrations/switch_as_x/) · [Remote: learn and send commands](https://www.home-assistant.io/integrations/remote/) · [Timer](https://www.home-assistant.io/integrations/timer/) · [Tuya (cloud)](https://www.home-assistant.io/integrations/tuya/) · [Backup](https://www.home-assistant.io/integrations/backup/) · [Backup emergency kit](https://www.home-assistant.io/more-info/backup-emergency-kit/)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [HACS](https://hacs.xyz): Home Assistant Community Store
- [Tuya Local](https://github.com/make-all/tuya-local) by make-all and contributors: local control of Tuya devices, including learning and sending IR/RF codes
- [Samba share app](https://github.com/home-assistant/addons/blob/master/samba/DOCS.md)
- Apple: [Set up a home hub](https://support.apple.com/en-in/102557)
