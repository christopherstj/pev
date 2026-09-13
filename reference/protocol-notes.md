# Bafang display UART protocol — distilled notes

Source: bbs-fw `extcom.c` (controller-side implementation) + bbs-fw wiki. The
laptop plays the **display** role (master). Controller only answers, never
initiates. Serial: **1200 baud, 8N1** over the green Higo display connector.

## Read requests (2 bytes, no checksum on request)

| Request | Meaning | Response | Parse |
|---|---|---|---|
| `11 08` | status | 1 byte | `00` OK, `01` pedaling, `03` brake active |
| `11 0A` | current | 2 bytes | `b0` = amps × 2, `b1` = checksum (== b0) |
| `11 11` | battery | 2 bytes | `b0` = battery %, `b1` = checksum (== b0) |
| `11 20` | speed | 3 bytes | `(b0<<8\|b1)` = wheel RPM, `b2` = (b0+b1+0x20) & 0xFF — the "weird checksum" |
| `11 22` | range field | 3 bytes | 2-byte BE value + sum checksum (stock: range; bbs-fw: temp or power, build option) |
| `11 24` | calories field | 3 bytes | stock: calories; **bbs-fw repurposes: battery voltage × 10** (2-byte BE + checksum) |
| `11 31` | moving? | 2 bytes | `0x31` moving / `0x30` still, doubled as checksum |

Speed → real units: `kph = rpm × wheel_circumference_m × 60 / 1000`.
The stock display does this conversion itself using its wheel-size setting; the
controller only ever reports RPM.

## Write requests (0x16 prefix, request carries trailing checksum)

| Request | Meaning |
|---|---|
| `16 0B <level> <ck>` | set PAS level (weird level codes: 0x00=0, 0x01=1, 0x0B=2, 0x0C=3, 0x0D=4, 0x02=5, 0x15=6, 0x16=7, 0x17=8, 0x03=9, 0x06=walk) |
| `16 0C ...` | set mode |
| `16 1A ...` | lights on/off |
| `16 1F ...` | speed limit |

Write-request checksum = sum of payload bytes after the `16 <opcode>` header,
truncated to 8 bits (per wiki; "full of inconsistencies" is the official vibe).

## Practical notes for Bethel (stock firmware)

- Reads are safe. Writes change ride behavior — leave alone until intentional.
- Watts: stock gives amps only (`11 0A`). Estimate W = amps × 52 (Luna pack
  nominal) until proven better; try `11 24` and see what stock actually returns.
- The green USB programming cable bridges the display power-latch line, so the
  controller wakes when the battery switch turns on — no display needed.
- Config-tool opcodes (`51`–`54`) exist on stock for reading/writing controller
  config (that's what BafangConfigTool uses). Different protocol family; ignore
  for sniffing.
