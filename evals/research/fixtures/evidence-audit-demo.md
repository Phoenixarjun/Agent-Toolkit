# Harbor Mobility \| Evidence review

**Research question:** How did two fictional service metrics change over the observed period?
**As of:** 2026-10-13
**Mode:** deep
**Outcome:** partial
**Independent review:** unavailable

> SYNTHETIC DEMO. The following data and sources are fictional, not externally verified.

## Answer

In the synthetic observations, on-time deliveries increased across the three months while resolved complaints also increased. These demo values illustrate report structure only.

## Findings

- **Delivery reliability improved in the sample:** The synthetic series shows a five percentage-point increase between July and September. ([C-001](#claim-c-001))
- **Complaint throughput increased in the sample:** The synthetic total rose by 40 cases; it does not establish whether customer experience improved. ([C-002](#claim-c-002))

## Claim ledger

<a id="claim-c-001"></a>
### C-001 | qualified

Fictional on-time deliveries rose from 88% to 93% over the observed three months.

**Sources:** [S-001](https://example.org/demo/deliveries)
**Verification:** Synthetic example values checked for internal consistency only
**Limitations:** Synthetic values only; no external source or independent agent verification.

<a id="claim-c-002"></a>
### C-002 | qualified

Fictional complaint resolutions rose from 120 to 160 in the same period.

**Sources:** [S-002](https://example.org/demo/support)
**Verification:** Synthetic example values checked for internal consistency only
**Limitations:** Synthetic values only; no external source or independent agent verification.

## Dated chart observations

### On-time deliveries by month

**Units:** %
**Method:** Original fixture observations, no interpolation

| Period | On-time deliveries |
| --- | --- |
| 2026-07-01 | 88 |
| 2026-08-01 | 90 |
| 2026-09-01 | 93 |

Synthetic observations; not a real performance series.

### Resolved complaints by month

**Units:** cases
**Method:** Original fixture observations, no interpolation

| Period | Resolved cases |
| --- | --- |
| 2026-07-01 | 120 |
| 2026-08-01 | 135 |
| 2026-09-01 | 160 |

Higher resolution count does not measure the number of incoming complaints.

## Question coverage

- **Q-001 (partial):** Did the synthetic on-time rate change? | Gap: No real-world evidence, fixture only.
- **Q-002 (partial):** Did resolved complaints change? | Gap: No real-world evidence, fixture only.

## Source register

- **S-001:** [Fictional delivery dashboard](https://example.org/demo/deliveries) | Synthetic Test Lab | accessed 2026-10-13 | Table A, rows July to September | Entirely fabricated for renderer and validation tests.
- **S-002:** [Fictional support dashboard](https://example.org/demo/support) | Synthetic Test Lab | accessed 2026-10-13 | Table B, rows July to September | Entirely fabricated for renderer and validation tests.

## Methods and limitations

Budget: 0/4 Scout tasks, 0/20 tool calls.

- Synthetic fixture. No independent agents actually ran and no external source was consulted. Context IDs are test records, not execution evidence.

Structural validation is not source-truth verification or an agent execution attestation.
