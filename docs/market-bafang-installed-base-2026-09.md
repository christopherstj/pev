# How many Bafang conversions exist?

Research report produced by "astra" for Chris, dated 16 September 2026 (delivered to the planning session 2026-09-15). Saved verbatim into the repo as the sourced basis for the market-size line in `sentry-product-v1.0.md` §2. Quantitative model covers shipments from 2015 through 2025 and estimates bikes remaining in use at the end of 2025.

**Assessment:** A worldwide installed base in the hundreds of thousands is plausible for Bafang BBS mid-drive conversions. Illustrative scenarios produce approximately **320,000–920,000 active converted bikes**, with a middle scenario around **590,000**. For informal planning, round this to **300,000–1 million**. These are conditional calculations, not a measured population or a statistical confidence interval. The historical shipment evidence is substantially stronger than the current installed-base estimate.

The scope is the BBS conversion family, including BBSHD. It excludes Bafang hub-motor conversions, whose aftermarket share I could not establish, and factory-built bikes using other Bafang systems. Consequently, this does not estimate every Bafang-powered bicycle or every kind of Bafang conversion.

**The strongest evidence comes from Bafang's Chinese IPO filings.** The 2018 filing reports 43,906 standard BBS motors sold in 2015 and describes this family as particularly associated with bicycle retrofits. Its product tables distinguish MAX, BBS, and BBS-HD. The 2019 filing extends the model breakdown through June 2019. Sources: [2018 IPO filing, especially pages 135 and 367–369](https://pdf.dfcfw.com/pdf/H2_AN201812281280410261_1.pdf), [2019 IPO prospectus](https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=5660185&stockid=603489).

| Period | All mid-drives sold | MAX sold | Standard BBS sold | BBSHD, calculated residual | BBS + BBSHD |
|---|---:|---:|---:|---:|---:|
| 2015 | 51,822 | 6,614 | 43,906 | 1,302 | 45,208 |
| 2016 | 103,615 | 43,177 | 52,757 | 7,681 | 60,438 |
| 2017 | 165,787 | 94,009 | 60,878 | 10,900 | 71,778 |
| 2018 | 262,928 | 163,201 | 85,561 | 14,166 | 99,727 |
| January–June 2019 | 143,782 | 103,451 | 32,094 | 8,237 | 40,331 |
| **Total** | **727,934** | **410,452** | **275,196** | **42,286** | **317,482** |

The BBSHD column is reconstructed as all mid-drives minus MAX minus standard BBS, using the filings' three-family classification. It is not a separately reported unit count. The combined column is all mid-drives minus MAX. Source for 2015: [2018 filing](https://pdf.dfcfw.com/pdf/H2_AN201812281280410261_1.pdf); source for subsequent periods: [2019 filing](https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=5660185&stockid=603489).

Thus, more than 317,000 motors in the relevant families had been sold in this documented window alone. This establishes historical product scale. It does not establish that 317,000 unique conversions were completed or remain operational: shipments can become new conversions, replacements, inventory, or assembled bikes.

**Later annual reports provide a usable denominator, but not a conversion count.** I located annual mid-drive sales through 2025. These include both aftermarket-oriented and factory-bike systems; I did not find an equivalent recent BBS/BBSHD unit split.

| Year | All Bafang mid-drive motors sold | Primary source |
|---|---:|---|
| 2019 | 308,622 | [2019 annual report, production/sales table](https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=6030271&stockid=603489) |
| 2020 | 396,811 | [2020 annual report, production/sales table](https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=7044125&stockid=603489) |
| 2021 | 553,330 | [2021 annual report, production/sales table](https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=8163134&stockid=603489) |
| 2022 | 510,453 | [2022 annual report, page 13](https://stockn.xueqiu.com/SH603489/20230420056661.pdf) |
| 2023 | 247,830 | [2023 annual report, production/sales table](https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10005733&stockid=603489) |
| 2024 | 167,839 | [2024 annual report, page 13](https://static.cninfo.com.cn/finalpage/2025-04-30/1223422806.PDF) |
| 2025 | 170,421 | [2025 annual report, page 12](https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-4/2026-04-29/12257199.PDF) |
| **Total** | **2,355,306** | Sum of the rows above |

Subtract 143,782 mid-drives sold in the first half of 2019, already covered by the detailed historical data. This leaves **2,211,524** mid-drives sold in the unclassified period, July 2019–December 2025.

The sharp change in total mid-drive sales after 2022 is a reason to avoid simply extrapolating early BBS growth indefinitely. It does not reveal how BBS demand itself changed.

**A reproducible installed-base model.** Three unknowns separate the reported shipments from the number of active conversions:

1. **Family share:** What proportion of later mid-drive shipments belonged to BBS/BBSHD?
2. **Distinct-conversion fraction:** What proportion of those motors resulted in a distinct completed aftermarket conversion, after excluding replacement motors, unsold/uninstalled stock, and factory-built applications?
3. **Retention:** What proportion of completed conversions remained in use at the end of 2025?

The calculation is:

`Active conversions = (317,482 + 2,211,524 × family share) × distinct-conversion fraction × retention`

| Input or output | Lower scenario | Middle scenario | Upper scenario |
|---|---:|---:|---:|
| Later BBS-family share — assumption | 20% | 30% | 40% |
| Distinct-conversion fraction — assumption | 70% | 80% | 90% |
| Retention — assumption | 60% | 75% | 85% |
| Estimated BBS-family motor shipments, 2015–2025 | 760,000 | 981,000 | 1,202,000 |
| Estimated distinct completed conversions | 532,000 | 785,000 | 1,082,000 |
| **Estimated active conversions, end of 2025** | **319,000** | **589,000** | **920,000** |

Outputs are rounded; additional digits would imply unjustified precision. The 20–40% family-share assumptions roughly surround the last observed mix: approximately 38% in 2018 and 28% in the first half of 2019, calculated from the historical table. They are not observations of later years. The conversion and retention assumptions are judgment calls; no representative measurements were found for them.

All three assumptions move together in these scenarios. This makes them useful for planning sensitivity, but they are not probability percentiles. A later family share below 20%, more replacement purchases, or lower retention could put the actual population below the range. Higher shares or retention could put it above. For example, 10% family share with the lower conversion and retention assumptions produces about 226,000 active bikes.

At the middle conversion and retention assumptions, each ten-percentage-point change in later family share changes the result by approximately 133,000 bikes. Resolving that model split would therefore improve the estimate materially.

The model omits pre-2015 conversions and 2026 additions and retirements. It applies aggregate retention instead of a survival curve by bike age. It also simplifies motors transferred between frames, repeated rebuilds, and bikes with multiple owners. It counts bikes, not unique people. The result should not be labeled a September 2026 census.

**Retail evidence is corroboration, not an independent global total.** Dillenger's BBS02 product page advertises more than 10,000 units sold worldwide, but the text does not clearly identify the reporting period or whether that means its own sales or the model overall. A Greenergia Amazon listing claims more than 5,000 motor sets sold worldwide across its business; it does not isolate a dated BBS conversion cohort. These support the existence of established sales channels, but I did not add them to manufacturer shipments or use them to calibrate the model. Sources: [Dillenger BBS02 listing](https://dillengerelectricbikes.com.au/products/bbs02-bafang-mid-drive-kit-b-series), [Greenergia listing and seller description](https://www.amazon.com/BAFANG-Optional-Conversion-Mountain-Commuter/dp/B0CQT6F43X).

Other tempting shortcuts are unsuitable: total Bafang motor production includes large factory-bike businesses; the financial category translated as "kits" includes electrical components rather than a clean count of retail conversion packages; distributor country and manufacturer export destination need not identify the final rider's country. Forum membership, reviews, search results, and general conversion-market revenue forecasts cannot supply a deduplicated installed-base count.

**What remains unknown.** I found no defensible current count for US-only Bafang conversions, active BBSHD-only bikes, unique owners, or bikes compatible with one particular sentry harness and communication protocol. Nor do these sales data measure emotional attachment, outdoor parking exposure, alarm demand, or willingness to pay. Bafang hub conversions expand the broader population, but their size and technical relevance need separate research.

**Implications for the sentry project.** The evidence supports a substantial enthusiast niche and strengthens the case for testing a Bafang-focused accessory. It does not yet establish a large paying market. Your learning goal and desire to protect a personally meaningful bike stand independently of the commercial estimate.

For a deterrence product, the commercially relevant population is the intersection of supported hardware, owners who park where they worry about theft, and people willing to install and pay for the device. Emotional value is a sensible interview hypothesis; it should not be converted into an assumed spending premium without testing.

The next useful research would be annual BBS01/BBS02/BBSHD sell-through by region from Bafang and several distributors, plus their replacement-versus-new-build mix. An anonymized survey of actual builders could then measure bike age, model, current use, parking exposure, existing deterrents, and purchase interest. No external outreach was conducted for this report.

For the plan, a defensible statement is: "Historical manufacturer disclosures document more than 317,000 BBS-family motors sold during 2015–mid-2019. A preliminary scenario model suggests a worldwide active BBS conversion population in the hundreds of thousands; its current size and the reachable sentry market remain unverified."
