# Option Evaluation

Evaluate candidates in two passes.

## Hard filters

Eliminate only when evidence shows a candidate is invalid under a fixed condition.

Typical hard filters:
- insufficient problem coverage
- hard-constraint violation
- unacceptable safety/legal/regulatory condition
- unavailable dependency
- impossible adoption requirement
- clearly unacceptable operating condition

Record the elimination reason.

## Comparative judgement

Select dimensions that can actually change the decision.

Possible dimensions:
- problem coverage
- simplicity
- implementation complexity
- initial and operating cost
- time-to-value
- adoption friction
- feasibility
- reliability
- security/privacy
- regulatory exposure
- maintainability
- reversibility
- scalability
- dependency risk
- experimentability

Do not mechanically use every dimension.

## Confidence

Prefer:
- assessment: LOW / MEDIUM / HIGH
- confidence: LOW / MEDIUM / HIGH
- basis: supporting evidence or reasoning

Numeric scoring is appropriate only when underlying inputs justify numeric comparison.

## Status quo

Include the current process or incremental improvement whenever credible.

The goal is to solve the problem, not guarantee a new product.

## Hybrids

Evaluate candidates independently before combining them.

A hybrid is justified only when:
- components solve complementary weaknesses
- the combined operating model remains coherent
- added complexity is lower than the value created

Treat the hybrid as a new candidate.
