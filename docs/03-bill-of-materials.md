# Bill of materials

What this setup cost in the author's home, a **3BHK apartment**. Prices are in ₹ including GST, from order history, except where a row says it is an online price.

## Core (needed for any setup)

| Item | Qty | Unit price (₹) | Line total (₹) | Where bought | Order date | Notes |
|---|---:|---:|---:|---|---|---|
| Raspberry Pi 4 Model B, 4 GB | 1 | 5,759 | 5,759 | Amazon | Aug 2025 | Runs Home Assistant OS |
| microSD card, 64 GB | 1 | 1,599 | 1,599 | Amazon | Aug 2025 | |
| Raspberry Pi power supply | 1 | 1,499 | 1,499 | Amazon | Aug 2025 | |
| UPS for the Pi | 1 | 2,999 | 2,999 | Amazon | Feb 2026 | Keeps it running through power cuts |
| Apple TV (home hub) | 1 | — | — | — | — | Already owned, so not counted. Apple Home needs a home hub for automations and remote access |
| **Core subtotal** | | | **11,856** | | | |

## Appliance control

| Item | Qty | Unit price (₹) | Line total (₹) | Where bought | Order date | Notes |
|---|---:|---:|---:|---|---|---|
| Aziot Wi-Fi IR blaster (Tuya "Smart IR") | 4 | 899 | 3,596 | Amazon | Sep 2025 | One per room with IR appliances |
| Tuya IR controller Pro (IR + RF) | 1 | 1,999 | 1,999 | Amazon | Sep 2025 | Also sends RF to both curtain motors |
| Tuya Wi-Fi switch module, 1-node | 5 | 699 | 3,495 | Amazon | Sep 2025 | Behind existing modular switches |
| Tuya Wi-Fi switch module, 2-node | 2 | 799 | 1,598 | Amazon | Sep 2025 | |
| Aziot Wi-Fi switch module, 4-node | 3 | 999 | 2,997 | Amazon | Sep 2025 | |
| Tuya smart plug, 16 A | 2 | 869 | 1,738 | Amazon | Sep 2025 | Geysers |
| Tuya smart plug, 10 A | 2 | 839 | 1,678 | Amazon | Sep 2025 | Two lamps |
| WiZ smart bulb, colour (RGBW) | 5 | 490 | 2,450 | — | — | Online price¹ |
| WiZ smart bulb, tunable white | 5 | 490 | 2,450 | — | — | Online price² |
| **Appliance control subtotal** | | | **22,001** | | | |

¹ Philips India online store, October 2026: 9 W B22 colour bulb, ₹980 for a pack of 2.
² No white-only WiZ bulb is currently listed in India, so these are priced as the colour bulb. That is an upper bound: white-only bulbs normally cost less.

## Total

| | ₹ |
|---|---:|
| **Complete build (core + appliance control)** | **33,857** |
| Without smart bulbs (used for the comparison below) | 28,957 |

## Comparison with commercial retrofits

What controlling the **same appliances** would cost with commercial retrofit products: 21 switched light circuits on 10 switchboards, 2 plug-in lamps, 2 geysers, 5 IR ACs, 4 IR fans and 2 curtains. Smart bulbs are left out on both sides, since they cost the same either way.

These are **estimates from published Indian prices (October 2026), not written quotes**.

| Option | Estimate (₹) | This build is cheaper by |
|---|---:|---:|
| **This build** | **28,957** | — |
| Wozart-based retrofit, installed³ | 1,37,007 – 2,83,485 | 4.7× – 9.8× |
| Aqara-type retrofit, 3BHK⁴ | 1,00,000 – 1,50,000 | 3.5× – 5.2× |
| Schneider Wiser retrofit, 3BHK⁴ | 2,00,000 – 3,00,000 | 6.9× – 10.4× |
| Turnkey installer, complete 3BHK⁵ | about 5,00,000 | about 17× |

³ **How the Wozart estimate is built:**

| Part | Basis | Low (₹) | High (₹) |
|---|---|---:|---:|
| 21 light circuits, 10 boards | Wozart Switch Controller (4 circuits, ₹9,899) on every board; the low case assumes the ₹6,599 Wozart Mini suits the 7 boards with 1–2 switches | 75,890 | 98,990 |
| 2 lamps | Smart relay or plug, ₹1,500–2,500 each | 3,000 | 5,000 |
| 2 geysers | Heavy-load switch, ₹1,500–2,500 each (Wozart's largest channel is 1,800 W, below a typical 2 kW geyser) | 3,000 | 5,000 |
| 5 ACs + 4 fans | One smart IR controller per room, ₹1,500–6,000 each (Wozart makes none) | 7,500 | 30,000 |
| 2 curtains | Smart curtain motor per track, ₹8,000–25,000 each | 16,000 | 50,000 |
| **Hardware** | | **1,05,390** | **1,88,990** |
| **Installed** | +30% (low) to +50% (high) for installation and wiring | **1,37,007** | **2,83,485** |

The comparison favours the retrofits slightly: they would replace curtain motors that this build reuses, and the installer figure covers more lighting circuits than this home has. The order of magnitude is the point.

### Sources

- Wozart prices and specifications: [Smartify, Wozart products](https://smartify.in/brand/wozart/) · [Wozart Switch Controller](https://smartify.in/product/wozart-switch-controller/)
- Price bands for relays, IR controllers and curtain motors; Aqara, Schneider Wiser and premium 3BHK tiers; installation at +30–50%: ⁴ [Smartify, Home Automation Cost in India 2026](https://smartify.in/blog/home-automation-cost-india-2026-guide/)
- ⁵ [AHA Smart Homes, 3BHK home automation cost breakdown](https://www.ahasmarthomes.com/blog/what-should-home-automation-cost)
- WiZ bulb price: [Philips India, Smart Wi-Fi 9W LED Bulb B22 (pack of 2)](https://in.shop.lighting.philips.com/products/philips-smart-wi-fi-9w-led-bulb-pack-of-2)

## Software

Home Assistant, HACS and every integration used here are free. No subscription is required.
