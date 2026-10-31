# Evidence and Prioritization Contract

Load only when a disputed finding, capacity claim, source provenance or high-severity recommendation needs additional rigor.

## Evidence levels

- `OBSERVED_SOURCE`: exact inspected code/config path at a stated repository revision. Supports claims about possible or deterministically reachable behavior; does not automatically measure runtime frequency or performance.
- `EXECUTED_CHECK`: recorded safe check with command/tool, environment, time, observed output or artifact and limitations. Check whether the instrument actually exercises the target condition.
- `RUNTIME_MEASUREMENT`: observed runtime/field/lab metric with workload, window, population, environment and collection method. Field and lab data are not interchangeable.
- `USER_REPORTED`: stakeholder report of experience or demand with date/basis; not independently measured.
- `INFERENCE`: reasoned hypothesis tied to supporting observations and explicit disconfirming evidence to seek.

Evidence can be stale, incomplete, environment-specific or contradictory. A test passing in an isolated unit environment does not prove end-to-end behavior or capacity. An empty log is not proof there were no failures unless instrumentation and sampling coverage are established. Reopen high-impact evidence in the original source; preserve disagreement when it cannot be resolved.

## Defect versus risk

- `CONFIRMED_DEFECT`: wrong behavior demonstrated for a relevant condition with credible direct evidence (reproduction or deterministic source path with corroborating facts). State the scope of confirmation.
- `SUPPORTED_RISK`: concrete reachable failure mechanism supported by specific evidence, but no direct observed failure under the target conditions.
- `HYPOTHESIS`: possible failure or bottleneck needing further diagnostic proof. Avoid numerical benefit, severity inflation and architecture prescriptions.
- `OPPORTUNITY`: a possible enhancement; may have no present user/business impact. Defer by default if no credible demand.

**Resource caution:** Unbounded storage growth is not necessarily a leak. Report an actual memory leak only with sufficiently specific retention/lifecycle or profiling evidence; otherwise call out resource-growth risk. For capacity, request actual peak concurrency/RPS, mix, resource ceilings and test conditions. If only daily/monthly users exist, capacity remains unverified.

## Priority and action gates

- `P0`: substantiated, active or imminently unavoidable critical impact on essential behavior/data/availability. Requires explicit direct evidence and consequence. Never assign to hypothetical forecasts or style concerns.
- `P1`: consequential defect or well-supported near-term risk requiring prioritization.
- `P2`: material bounded concern that should follow immediate commitments.
- `P3`: minor localized issue or improvement; generally defer.

Keep **priority** distinct from **confidence**: a low-confidence catastrophic possibility may justify investigation, not a P0 remediation claim. If evidence is too weak to set a defensible priority, record `UNRATED` and propose a cheap probe instead of an architecture change.

Classify recommended action as `NOW`, `NEXT`, `DEFER`, `NO_CHANGE`. `NOW` must have confirmed or well-supported material impact or a mandatory user requirement; `DEFER` must explain the trigger for reconsideration. When no action is justified, say so.

A minimally sufficient recommended fix has a clear owner, affected boundary, expected effect, proof method, and estimated qualitative complexity. Don't make cost or performance claims with invented percentages.

## Cross-check the report

1. Every top action corresponds to a traceable finding with actual relevant impact.
2. Every P0 has credible direct evidence and an affected essential function.
3. Every proposed major redesign cites a real limiting requirement and compares a simpler credible alternative.
4. Every numerical capacity claim identifies provenance and workload context.
5. Every absent capability or healthy subsystem is supported by declared inspection scope, not assumed from silence.
6. Every `NOT_APPLICABLE` category states why the application does not possess that boundary today.
7. Every question asks for a user-owned decision or external fact with a named downstream consequence.
8. Every independent-verification claim identifies a genuine separate context or is downgraded.
