# The problem

## Smart homes in India, and Apple Home

Most Indian homes already have the appliances worth automating: modular wall switches, ceiling fans, split ACs, geysers, curtains. Almost none of them can talk to Apple Home.

- **Apple Home-certified devices are scarce and expensive in India.** Few brands sell them here, and most of what is sold is aimed at other ecosystems.
- **Professional retrofits cost lakhs.** Installer packages replace switch plates, add hubs and proprietary controllers, and lock the home into one vendor. For the same appliances in a 3BHK, published Indian prices put a retrofit at roughly ₹1.4–2.8 lakh with Wozart, and a turnkey installation at about ₹5 lakh. This project did it for **₹28,957** in hardware (₹33,857 including smart bulbs); see [03-bill-of-materials.md](03-bill-of-materials.md).
- **The affordable devices are Tuya-based** (sold under dozens of brand names): Wi-Fi switch modules that fit behind existing switches, smart plugs, and IR/RF blasters. They are cheap and widely available, but they are built for the Smart Life app and the Tuya cloud, not Apple Home.
- **ACs and fans are infrared-only.** They have no network connection at all. Tuya's IR library only knows some remotes: if your AC model isn't recognised, Smart Life can't even offer it as an AC.

## What this project does

It makes those affordable devices behave like native Apple Home accessories, using Home Assistant on a Raspberry Pi as the bridge:

| In the home | In Apple Home |
|---|---|
| Tuya switch module behind an existing switch | A light tile |
| Tuya smart plug on a geyser | A switch with a restart-safe automatic cut-off |
| IR-only split AC (any brand, recognised by Tuya or not) | A thermostat tile: cool, off, temperature |
| IR ceiling fan | A fan tile with power and 5 speeds |
| RF curtain motor | A curtain tile with open, close, stop |

Everything runs over the home network: it keeps working when the internet is down, and responds roughly twice as fast as the cloud (see [07-local-control.md](07-local-control.md)).

## Design goals

1. **Affordable.** Off-the-shelf Tuya hardware, a Raspberry Pi, and free software. Costs from real receipts are in [03-bill-of-materials.md](03-bill-of-materials.md).
2. **No rewiring.** Switch modules fit behind existing switches; IR and RF appliances are untouched.
3. **Native Apple Home.** Real tiles, Siri, Apple Home automations, shared with family. No extra app to learn.
4. **Works for any IR AC.** Codes are learned from the AC's own remote, so it doesn't matter whether Tuya recognises the brand.
5. **Local first.** No dependency on the Tuya cloud or the internet once set up.
6. **Safe.** Appliances such as geysers switch themselves off even across power cuts and restarts.
7. **Reproducible.** Blueprints and copy-and-rename examples, validated automatically on every change.

## What it doesn't do

- **IR and RF are one-way.** An AC or fan can't report its real state; Home Assistant remembers what it last sent. Using the physical remote makes the two drift apart until the next command from Apple Home.
- **Some Tuya devices can't be controlled locally.** A few report too little to be identified (see [07-local-control.md](07-local-control.md), section 6); they can stay on the cloud or be replaced.

## Read next

- [02-architecture.md](02-architecture.md): how the pieces fit together
- [04-setup-guide.md](04-setup-guide.md): build it yourself
