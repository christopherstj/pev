# SENTRY FOR CONVERTED E-BIKES — Product Document v1.0

Status: Pre-product. Everything ships on Bethel (reference bike) first. Purpose of this doc: single source of truth for product decisions, to be used as context in build/code sessions. Companion docs: `product_spec_v0.1.md` (subsystem spec), `pev_fleet_project.md` (repo architecture), `bethel_parts_and_costs.md`, `bethel_tools_list.md`.

Authored by Chris, 2026-09-14 (90-minute planning session, drive to LA). Saved verbatim into the repo by the planning session so build sessions can load it.

## 1. One-liner and positioning

"It scares them off — and if they take it anyway, you know exactly where it went."

Aftermarket smart security for e-bikes people already own, starting with the Bafang conversion community. Local-first, no mandatory subscription, open source, repairable. Deterrence-first hierarchy: 1) Deter → 2) Recover → 3) Document. The camera is the third layer, never the headline promise. Never marketed as "prevents theft" or "catches thieves."

Origin story (use once, in README, never perform it): founder's headlights were stolen off the reference bike overnight, mid-design.

## 2. Market facts (researched, cited in chat log 2026-09-14)

* US e-bike sales ~1.48M units/yr (2025), installed base est. 6–9M; fastest-growing price band $2.5k–3.5k. EU several× larger.
* E-bikes stolen ~3× the rate of regular bikes; average stolen e-bike $1,500–5,000.
* Bafang conversion installed base: est. hundreds of thousands globally; active enthusiast tier tens of thousands; hardcore (flashes firmware) thousands. Beachhead = hardcore + enthusiast tiers.
* Incumbent gaps: PowUnity BikeTrax = GPS only, subscription after yr 1, bare-wire "Universal" for non-OEM bikes, no camera/immobilization. Cycliq/Garmin = ride dashcams, 5–7hr batteries, off when parked.
* Concept validation / competition (important corrections): Tarran L1 (new premium e-bike) ships integrated Sentry Mode + locking SyncStand + camera add-on — validates demand, starts the OEM clock (~3–5 yr differentiation window on new bikes). Sentidrive Sentinelle does aftermarket camera-sentry for motorcycles. Nobody does retrofit e-bike sentry with on-device ML. Confidence: high, not certain — sweep Kickstarter/Alibaba/Eurobike lists before serious capital.
* The installed base never gets OEM features (dashcam precedent) — retrofit demand outlives the differentiation window.

> **Sourced update (2026-09-15, see `market-bafang-installed-base-2026-09.md`):** Bafang's IPO filings document **317,482 BBS + BBSHD motors sold 2015–mid-2019**; a scenario model puts the worldwide *active* BBS-conversion population at roughly **320k–920k (middle ~590k)** at end-2025 — conditional, not measured. Bafang's total mid-drive sales fell from 553k (2021) to 170k (2025), so treat the base as a large *stock* with shrinking inflow. Unverified: US share, BBSHD-only count, UART-vs-CAN split (post-2020 kits can be CAN; the v1 harness is UART), willingness to pay. The "serviceable market ≈ 1–2M US owners" line in §5 is the *e-bike* TAM, not the Bafang beachhead; the beachhead SAM is realistically tens of thousands of reachable US owners.

## 3. Product pillars (from spec v0.1, updated)

1. Deter — 110dB siren; visible deterrence screen (e-paper/OLED: "⚠ SENTRY ACTIVE — RECORDING" + red LED pulse, wakes on person detection). Deterrence screen is cheap ($8–15 BOM) and disproportionately valuable.
2. Recover — GPS is the v1 hero. Base tier: ride logging + BLE recovery, $0/mo forever. Cellular tier: live tracking + remote alerts, at-cost sub ($3–5/mo), device fully functional without it.
3. Document — dual wide-FOV cameras (front bars + rear deck; no stitched 360 — that's smartphone-SoC territory). Sentry stills + IMU-triggered burst; ride mode loop-record to SD with incident locking. Night capability is make-or-break: quality sensor + IR. Evidence packet export: timestamped photos + GPS trail + serial → police-report/insurance-ready PDF + Bike Index listing (one-tap "report stolen").
4. Alarm intelligence — on-device ML (ESP32-S3, LiteRT/TFLM, int8): IMU time-series classifier {bump-and-go, wind, truck rumble, dog, lift-and-carry, rolling, grinder/cutting vibration} + camera person-vs-dog-vs-car confirmation. False-positive rate is the product's central KPI.
5. Access/response — BLE challenge-response arm/disarm (phone + fob), RSSI hysteresis. Alert flow: push + instant still → 15–30s disarm countdown → siren fires by default (fail-loud). Live view on demand: LTE Cat-1 (not Cat-M1 — bandwidth), low-res 60s sessions.
6. Immobilize (later phase) — motor lockout via Bafang protocol; motorized center-stand deadbolt (stand deployed = wheel up; bolt locks stand down; limit-switch interlock; manual key fallback mandatory; no spoke contact ever).
7. Hard-target requirement — every component on tamper loops (removal = alarm), security fasteners, through-frame mounts. The security device must not be stealable.

## 4. Decided: NO (do not revisit without strong cause)

* No facial recognition — not as feature, not via third-party lookup. Device captures evidence; identification is police's job. CA legal environment hostile; one wrong match = company-ending.
* No name-and-shame social board — crowdsourced human identification misfires (Boston/Reddit, Citizen precedents); defamation + harassment platform liability; brand-fatal. Community energy goes to bike-recovery instead (Bike Index integration).
* No mic / mic-off default — CA two-party consent.
* No spoke-engaging lock — stand deadbolt only.
* No cloud dependency for core function — device useful forever if company dies. Footage local by default; leaves device only on confirmed incident.
* No competing on price with future clones — moat = trained classifier + fleet data flywheel + harness library + community trust.

## 5. Unit economics (planning numbers)

* BOM $130–200; landed COGS ~$200 (assembly, test, duty, scrap).
* Retail $499–649 (60–70% gross) — matches category norms (Cycliq bundle, Garmin Varia Vue, Insta360).
* Effective net after processing/shipping/warranty/amortized fixed: ~$290/unit at $600.
* Tiering: bare board + firmware ~$180–250 (community/marketing tier, thin margin) | full kit $600 (the business) | installed tier: later, maybe never.
* Serviceable market: US urban owners of $1,500+ bikes ≈ 1–2M; 0.5–1% share = 5–20k units/yr = $2.5–12M revenue ceiling. Tinkerer-phase reality: 100–500 kits/yr, $30k–145k net.
* Compliance from day one: pre-certified ESP32/LTE modules, modular FCC path. LLC + product liability insurance before unit one sells.

## 6. Premortem — ranked kill risks & mitigations

1. False alerts → users disable notifications → dead product. Mitigation: ML classifier IS the product; months of labeled real-world data pre-launch; per-user sensitivity; beta cohort diversity.
2. Useless night footage → broken promise. Mitigation: spend on sensor + IR; market only real night captures.
3. Battery drain incident → "it bricked my commute" forum post. Mitigation: hard low-voltage cutoff well above pack floor, watchdogs, per-release current-budget tests. Sleep architecture: ESP32 sentry always-on (µA-mA), gates Pi/LTE power via MOSFET.
4. Support matrix eats founder → one harness SKU at launch (Bafang UART), docs-first, community front-line, batch size capped to founder evenings.
5. Evidence disappoints (police don't chase) → position as deter/recover/document stack, never "catch thieves."
6. Legal → FCC via modules; no mic; immobilizer ships later with interlocks; terms promise deterrence not prevention.
7. Clones + OEM creep → accept; moat is data flywheel + trust; don't price-race.
8. Ops: dual-source camera/LTE modules; tariff headroom in price; Cat-M1/Cat-1 carrier longevity.

## 7. Data strategy — community as labeling infrastructure

* Every alert gets one-tap label in app: {wind, bump, dog, person-benign, attempted theft, other}.
* Beta units to forum builders = diverse parking environments = training-set generator. Contributions credited in release notes; classifier improvement arc documented publicly.
* Bethel parked downtown = patient zero dataset (incl. genuine accessory-theft class, unfortunately validated).
* Instrument generously from day one: current data logger doubles as training-set collector.

## 8. Sequencing (hard order, do not skip)

Phase A — Bethel v1 (now): brake lights working on-bike + headlight installed (hardened mount — it was stolen once). Founder builds EE comfort. Nothing security-critical yet.
Phase B — Bethel security: IMU alarm + siren + BLE arm/disarm + GPS logging + tamper loop. Data logging begins.
Phase C — ML: alarm classifier v1 (Edge Impulse pass, then by-hand pass: FFT features, QAT, memory budget). Then camera person-detect. Then crash detect.
Phase D — Community phase: ES build thread + GitHub public + beta kits to builders. This phase retires risks 1–4. NOT a smaller version of the business — the risk-retirement program for it.
Phase E — Product phase: full kit, $600 tier, evidence-packet feature, cellular tier. Stand deadbolt and PIN display trail behind on their own tracks.

## 9. Go-to-market (persona-free, per founder constraint)

* Anchor: one Endless Sphere build thread ("Bethel: BBSHD cargo bike gets a brain"). Update on substance, never schedule. Show failures + fixes.
* GitHub repo public from day one — firmware, schematics, protocol notes; README carries origin story once.
* Reddit: 2–3 finished-milestone photo posts/yr on r/ebikes-type subs; never "follow me."
* Hackaday.io project + tips-line email at demo-able milestone; single Show HN when repo is interesting.
* Presence in bbs-fw thread/discussions as helpful user = pre-sold audience.
* Norms: substance cadence; lead with problem not product; disclose commercial intent explicitly and use vendor sections when selling starts.
* Success threshold: 100–300 engaged followers = first batch + labeling cohort. That's a workshop, not an audience.

## 10. Open questions

* Live-view radio: Cat-1 on every unit vs. cellular-tier SKU split (BOM +$10–15).
* Deterrence screen: e-paper (sunlight, persistent, low power) vs OLED (cheaper, brighter at night).
* Rear camera placement on non-cargo bikes (seatpost? rack-dependent?) — affects harness/SKU discipline.
* Bike Index integration API scope for v1 evidence packet.
* Name. (Not urgent. The ES thread doesn't need one.)
