# Project history

How this setup grew, dated from Home Assistant's own records: the creation timestamps of integrations, entities and automations, and the learned scenes stored with them. Nothing here is reconstructed from memory.

## 2025

| Date | Milestone |
|---|---|
| 6 Aug | Home Assistant OS installed on a Raspberry Pi 4 |
| 10 Aug | Tuya (cloud), WiZ bulbs and the **HomeKit Bridge** set up: Tuya switches and WiZ lights appear in Apple Home. First learned RF scenes for **two curtains**, and the first IR fan scenes |
| 11 Aug | **First IR fans as Apple Home fan tiles** (template fans with power and 5 speeds), for two rooms |
| 12 Aug | **First IR AC as an Apple Home thermostat**: `generic_thermostat` with a dummy heater and a virtual temperature sensor, driven by learned IR scenes |
| 21 Aug | Second AC with a **full learned temperature range** (16–30 °C as complete states) |
| 26 Aug | Raspberry Pi health monitoring (power-supply checker) |
| 21–23 Sep | Scaled to **5 ACs and 4 fans** across the home: three more ACs and two more fans, with their scenes learned |
| 18 Oct | Additional learned AC mode (quiet) |
| 23 Oct | Tenth WiZ bulb |

## 2026

| Date | Milestone |
|---|---|
| Jan | Last Tuya switch modules added (28 cloud switch and light entities in total) |
| 15 Feb | **Curtains as Apple Home curtain tiles** (template covers with remembered position); light groups; TVs and media players integrated |
| 18 Feb | Matter devices added |
| 21 Feb | First switch exposed to Apple Home as a light (switch → light conversion) |
| 15–16 Mar | Two ACs re-learned with full temperature ranges |
| 1 Apr | Remaining ACs' learned temperature ranges completed |
| 3 Apr | HACS installed (community integrations) |
| 30 Apr – 13 May | Robot vacuum integrated; cleaning schedules by day (carpet / no-carpet days) on 7 May |
| 5 Jul | **First geyser safety automation** (automatic cut-off) |
| 11–12 Oct | **Audit and hardening:** crash investigation and fix ([06](06-crash-case-study.md)); AC logic rebuilt as the reusable `ir_ac_bridge` blueprint; fan speeds moved to a queued script; restart-safe geyser timers for both geysers; unused cloud voice assistants and remote access turned off |
| 13 Oct | **Local control** ([07](07-local-control.md)): 22 light channels, 2 geysers and a plug moved to Tuya Local; 5 IR/RF blasters added; 115 learned scenes replaced by local codes; local-first sending with cloud fallback; alerts for unreachable devices. The system now works without internet |
| 13 Oct | This repository: blueprints, examples, validation, privacy scan, and these docs |
